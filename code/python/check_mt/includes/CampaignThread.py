from includes.RootLogger import rootLogger
import traceback
import datetime
import concurrent.futures
import time
import threading

from includes.SMTPSocks import MYSMTP, MYSMTP_SSL
from includes.SMTPThread import SMTPThread

# campaign state constants
CS_CREATED = 0
CS_PROCESSING = 1
CS_PAUSED = 2
CS_HIBERNATED = 3
CS_COMPLETED = 4
CS_DELETED = 5

# campaign REQ_MARK behaviours
FB_SET_FAIL = 0
FB_SET_NULL = 1

# every processed task behaviour
RS_NEW = 0
RS_PROCESSING = 1
RS_SUCCESS = 2
RS_FAILED = 3
RS_SKIPPED = 4
RS_BLACKLIST = 5

class CampaignThread(threading.Thread):
    def __init__(self, campaign, socks=[], settings=None, my_redis=None, threadLock=None, attachements=[], macro_data=[], accounts=[]):
        self.campaign = campaign
        # self.prefix = prefix
        self.started_at = None
        self.socks = socks
        self.settings = settings
        self.my_redis = my_redis
        self.status = CS_PROCESSING
        self.accounts = accounts
        self.threads = []
        self.threadLock = threadLock
        self.attachements = attachements
        self.macro_data = macro_data

        self.prefix = f"Campaign[{self.campaign.id}]:"

        self.result = {"_id": campaign.id, "status": self.status, "updated_at": None, "finnished_at": None}
        # startt regular
        threading.Thread.__init__(self)

    def run(self):
        self.started_at = time.time()
        rootLogger.info(f"{self.prefix} Begin campaign")
        # generate as many workers as nneded

        # run untill it's either ends or just paused, thou if paused, we don't give a fuck for that
        while True:
            # remove dead threads from list
            live_threads = [thread for thread in self.threads if thread.isAlive()]
            dead_threads = [thread for thread in self.threads if not thread.isAlive()]

            # for dead threads, extract sock and apply to others...

            self.threads = live_threads

            # generate missing threads for campaign
            self.appendWorkers()

            # check whether it's time to stop or not
            if len(self.threads) < 1:
                rootLogger.info(f"{self.prefix} all threads are finnished, marking as done and exit")
                self.status = CS_COMPLETED
                break
            elif self.status != CS_PROCESSING:
                # mark all threads as done and exit
                rootLogger.info(f"{self.prefix} marked as done from Main or UI, stop smtp-threads and exit")
                for thread in self.threads:
                    # this one if necessearly only because of tests
                    stop = getattr(thread, "stop", None)
                    if callable(stop):
                        thread.stop()
                        # stop(thread)

                break

            time.sleep(5)
            rootLogger.info(f"{self.prefix} work in progress ({len(self.threads)} active workers)")

            # # FIXME: remove after tests
            # if time.time() - self.started_at > 15*60:
            #     self.threads = []
            #     rootLogger.info(f"{self.prefix} simulate all threads are finnished")

        self.result.update({"status": CS_COMPLETED, "updated_at": datetime.datetime.utcnow(), "finnished_at": datetime.datetime.utcnow()})

    # controlling from outside
    def stop(self, force=False):
        self.status = CS_PAUSED if force else CS_COMPLETED

    def appendWorkers(self):
        # if amount of thread is lower than

        while len(self.threads) < int(self.settings['workers_per_campaign']):
            try:
                account = next(self.accounts)

                rootLogger.info(f"{self.prefix} got new account from self.acocunts:{account.id}")
                # create new smtp-sender thread
                new_thread = SMTPThread(
                    campaign = self.campaign,
                    account=account,
                    socks = self.socks,
                    settings = self.settings,
                    my_redis = self.my_redis,
                    threadLock = self.threadLock,
                    attachements = self.attachements,
                    macro_tpls = self.macro_data)

                new_thread.daemon = True
                new_thread.start()

                self.threads.append( new_thread )

            except Exception as e:
                rootLogger.error(f"{self.prefix}[run][appendWorkers]:{e}")
                # raise e
                break

        # if amount of thread is higher than settings, just finish first few
        if len(self.threads) > int(self.settings['workers_per_campaign']):
            kill_amount = len(self.threads) - int(self.settings['workers_per_campaign'])
            kill_threads = self.threads[0:kill_amount]

            for thread in self.threads:
                # this one if necessearly only because of tests
                stop = getattr(thread, "stop", None)
                if callable(stop):
                    thread.stop()


    def updateSettings(self, _new_settings):
        # make copy of settings
        self.settings = dict(_new_settings)
        for thread  in self.threads:
            if thread.isAlive():
                thread.updateSettings( _new_settings )

    def updateSocks(self, _new_socks):
        # commonly i hope just to overwrite here as all child threads uses same list

        current_socks_ids = [item['id'] for item in self.socks]
        # append items
        append_new = [item for item in _new_socks if item['id'] not in current_socks_ids]

        # remove items
        new_socks_ids = [item['id'] for item in _new_socks]
        removal_ids = [item['id'] for item in self.socks if item['id'] not in new_socks_ids]

        self.threadLock.acquire(blocking=True, timeout=300)
        try:

            # remove bad items
            for item in self.socks:
                if item['id'] in removal_ids:
                    self.socks.remove( item )

            # append new items
            self.socks.extend( append_socks )

        except Exception as e:
            rootLogger.error(f"{self.prefix}[updateSocks]:{e}")
        finally:
            if self.threadLock.locked():
                self.threadLock.release()
