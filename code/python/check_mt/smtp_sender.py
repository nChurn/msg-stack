
import tracemalloc
# Store 25 frames
# tracemalloc.start(25)
# start = tracemalloc.take_snapshot()
# start = start.filter_traces((
#     tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
#     tracemalloc.Filter(False, "<frozen importlib._bootstrap_external>"),
#     tracemalloc.Filter(False, "<unknown>"),
# ))

import socket, requests, time, datetime, threading
import concurrent.futures

# from includes.SMTPSocks import MYSMTP, MYSMTP_SSL
# from includes.IMAP4Socks import MYIMAP4, MYIMAP4_SSL
# from includes.POP3Socks import MYPOP3, MYPOP3_SSL
from includes.ProtocolErrors import retry_list, socket_errors, auth_error_list, wrong_ssl_list
import includes.Database as db
from includes.RootLogger import rootLogger
from includes.CampaignThread import CampaignThread, CS_CREATED, CS_PROCESSING, CS_PAUSED, CS_HIBERNATED, CS_COMPLETED, CS_DELETED


import traceback
import random
import ssl
import re

import os
from os.path import join, dirname
from dotenv import load_dotenv
import redis
import sys

def show_malloc():
    # snapshot = tracemalloc.take_snapshot()
    # top_stats = snapshot.statistics('traceback')

    # # pick the biggest memory block
    # # stat = top_stats[0]
    # # rootLogger.info("%s memory blocks: %.1f KiB" % (stat.count, stat.size / 1024))
    # # for line in stat.traceback.format():
    # #     rootLogger.info(line)
    # # snapshot = tracemalloc.take_snapshot()
    # # for i, stat in enumerate(snapshot.statistics(‘filename’)[:5], 1):
    # # logging.info(“top_current”,i=i, stat=str(stat))

    # current = tracemalloc.take_snapshot()
    # current = current.filter_traces((
    #     tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
    #     tracemalloc.Filter(False, "<frozen importlib._bootstrap_external>"),
    #     tracemalloc.Filter(False, "<unknown>"),
    # ))
    # stats = current.compare_to(start, 'filename')
    # for i, stat in enumerate(stats[:10], 1):
    #     # rootLogger.info("since_start:", i=i, stat=str(stat))
    #     rootLogger.info(f"since_start: {i}: {stat}")

    from webmails.WebMailClass import display
    if display.is_started:
        display.stop()


# # get socks, make some changes
def getSocksList(socks):
    # with threadLock:
    # threadLock.acquire(blocking=True, timeout=300)
    try:
        db_socks = db.getSocks(socks_type="spam", row_as_dict=True, alive_only=True, allow_smtp_only=True, enabled_only=True)
        # mark all processes are zero
        for item in db_socks:
            item['processes'] = 0
            # try to get proxy from original list
            proxy = next( (old_item for old_item in socks if old_item['id'] == item['id']), None)
            if proxy is not None:
                item['processes'] = proxy['processes']
    except Exception as e:
        # raise e
        rootLogger.error(f"[getSocksList]: {e}")
    # finally:
    #     if threadLock.locked():
    #         threadLock.release()

    return db_socks

def updateAttachements(threads):
    if len(threads) < 1:
        return True

    all_attachements = []
    for thread in threads:
        all_attachements.extend(thread.attachements)

    # make em unique
    unique_attachements = list({v['id']:v for v in all_attachements}.values())
    # prepare dict values for update:
    upd_attachements = [{'_id': item['id'], 'used': item['used'], 'updated_at': datetime.datetime.utcnow()} for item in unique_attachements]

    db.updateCampaignAttachements(upd_attachements)

def syncCampaigns(threads=[], chunk_size=5, socks=[], settings=None, my_redis=None, threadLock=None):
    # update attachements uasge statistics
    updateAttachements(threads)

    # update settings, as well as socks
    for thread in threads:
        thread.updateSettings( settings )
        thread.updateSocks( socks )

    upd_campaigns = [{'_id': thread.campaign.id, 'workers': len(thread.threads) , 'updated_at': datetime.datetime.utcnow()} for thread in threads]
    # rootLogger.info(f"[Main][syncCampaigns] upd_campaigns:{upd_campaigns}")
    db.updateCampaigns(upd_campaigns)

    # get all campaigns from database
    db_campaigns = [item for item in db.getCampaigns(status=CS_PROCESSING)]

    # make filtrations:
    db_campaign_ids = [campaign.id for campaign in db_campaigns]
    th_campaign_ids = [thread.campaign.id for thread in threads]

    # threads that are being executed and not changed outside
    normal_threads = [item for item in threads if item.campaign.id in db_campaign_ids]

    # threads that are still running but marked outside as paused
    kill_threads = [item for item in threads if item.campaign.id not in db_campaign_ids]

    # stop all kill_threads
    for thread in kill_threads:
        thread.stop(force=True)

    # free memory from that threads
    del kill_threads[:]

    # refresh macros data to fill new threads with fresh macroses
    macro_data = db.getMacroTemplates(my_redis)

    # list of campaigns that set for execution from outside, but no threads for them
    new_campaigns = [item for item in db_campaigns if item.id not in th_campaign_ids]

    # generate new threads and add them to list, ignoring so far executing campaigns
    # while len(normal_threads) < chunk_size and len(new_campaigns) > 0:
    while len(new_campaigns) > 0:
        campaign = new_campaigns.pop()
        rootLogger.info(f"[Main][syncCampaigns]: Generate new campaign processor:{campaign.id}")

        # provide attachements
        attachements = []
        if campaign.has_attaches > 0:
            attachements = [dict(item) for item in db.getCampaignAttachements(campaign.id)]
            # rootLogger.info(f"[Main][syncCampaigns]: attachements:{attachements}")

        # accounts
        accounts = db.getCampaignAccounts(campaign.id)

        new_thread = CampaignThread(campaign, socks=socks, settings=settings, my_redis=my_redis, threadLock=threadLock, attachements=attachements, macro_data=macro_data, accounts=accounts)
        new_thread.daemon = True
        new_thread.start()

        normal_threads.append( new_thread )

    # TODO: decide if stop on LIFO or FIFO based rule
    # stop and remove threads that are too much for current max amount of campaigns
    while len(normal_threads) > chunk_size:
        rootLogger.info(f"[Main]: active threads({len(normal_threads)}) are more than chunk_size({chunk_size})")
        thread = normal_threads.pop()
        kill_threads.append( thread )

    # kill exra threads
    for thread in kill_threads:
        thread.stop(force=True)

    # update database campaigns status
    if len(kill_threads) > 0:
        db.updateCampaigns([{'_id': thread.campaign.id, 'status': CS_PAUSED, 'workers': 0, 'updated_at': datetime.datetime.utcnow()} for thread in kill_threads])

    return normal_threads

if __name__ == "__main__":
    sleep_minutes = 0.5
    start_time = time.time()
    rootLogger.info("[Main]: Begin")

    # sleep_time = 5 * 60
    # rootLogger.info(f"[Main]: Sleep for {sleep_time/60} minutes and start again")
    # show_malloc()
    # time.sleep(sleep_time)
    # sys.exit(0)

    # just for easy check if we need to do any actions at all
    db_campaigns = []
    try:
        # get all campaigns from database
        db_campaigns = [item for item in db.getCampaigns(status=CS_PROCESSING)]
    except Exception as e:
        rootLogger.error(f"[Main]: db.getCampaigns:{e}, quit and sleep")
        db_campaigns = []
    finally:
        if len(db_campaigns) < 1:
            sleep_time = sleep_minutes * 60
            rootLogger.info(f"[Main]: No started campaigns, sleep for {sleep_minutes} minutes and start again")
            show_malloc()
            time.sleep(sleep_time)
            sys.exit(0)

    settings = None
    # get system settings
    try:
        settings = db.getSystemSettings()['campaign']
    except Exception as e:
        rootLogger.error(f"[Main]: getSystemSettings:{e}, quit and sleep")
        sleep_time = 5 * 60
        rootLogger.info(f"[Main]: Sleep for {sleep_time/60} minutes and start again")
        show_malloc()
        time.sleep(sleep_time)
        sys.exit(0)
    # rootLogger.info(f"[Main]: System settings: {settings}")

    # socks check interval
    sci = int(settings['cmp_check_interval'])

    # mark last check so first loop iteration get all necessearly data
    last_check = time.time() - sci*1.2

    env_host = os.getenv('REDIS_HOST', default=None)
    if env_host is None:
        # Create .env file path.
        dotenv_path = join(dirname(__file__), 'includes/.env')
        # Load file from the path.
        load_dotenv(dotenv_path)

    # create redis instance
    env_host = os.getenv('REDIS_HOST')
    env_port = int(os.getenv('REDIS_PORT'))
    env_password = os.getenv('REDIS_PASSWORD') if os.getenv('REDIS_PASSWORD') != 'null' else None
    env_decode_responses = True if os.getenv('REDIS_DECODERESPONSES') == 'True' else False
    env_max_connections = int(os.getenv('REDIS_MAX_CONN', default=1024))

    # Use a thread-safe blocking connection pool.
    redis_conn_pool = redis.BlockingConnectionPool(
        host=env_host,
        port=env_port,
        max_connections=env_max_connections,
        decode_responses=env_decode_responses,
        timeout=300,
    )

    # redis instance will share among all futher processes
    my_redis = redis.Redis(connection_pool=redis_conn_pool, decode_responses=env_decode_responses)

    # will socks
    socks = []
    # will contain campaign threads
    threads = []
    # threadlock for campaign sync etc
    threadLock = threading.Lock()

    rootLogger.info("[Main]: Enter main loop")
    while True:

        # check some values
        now = time.time()
        if now - last_check > sci:
            last_check = time.time()
            rootLogger.info("[Main]: time to update settings and sync campaigns")
            # with threadLock:
            threadLock.acquire(blocking=True, timeout=300)
            try:
                settings = db.getSystemSettings()['campaign']
                # rootLogger.info(f"[Main]: settings: {settings}")

                socks = getSocksList(socks)
                # rootLogger.info(f"[Main]: socks: {socks}")
                # update common variables
                sci = int(settings['cmp_check_interval'])
                chunk_size = min(int(settings['max_active_campaigns']), len(socks)*int(settings['connection_per_proxy']))

                rootLogger.info(f"[Main]: chunk_size:{chunk_size}, sci:{sci}")

                # resync all data
                # rootLogger.info("[Main]: sync campaign threads")
                threads = syncCampaigns(threads, chunk_size, socks, settings, my_redis, threadLock)

            except Exception as e:
                # raise e
                # rootLogger.error(f"[Main]: Refresh settings and socks:{traceback.format_exc()}")
                rootLogger.error(f"[Main]: Refresh settings and socks:{e}")
            finally:
                if threadLock.locked():
                    threadLock.release()

        # check results for all threads
        done_threads = []
        for idx, thread in enumerate( threads ):
            if not thread.isAlive():
                rootLogger.info(f"[Main]: {thread.prefix} done, get results")
                threads.pop(idx)
                done_threads.append(thread)

        if len(done_threads):
            # check if campaign still has records to process, this happens when campaign got new records on fly
            for thread in done_threads:
                if len( db.getCampaignRecords( thread.campaign.id, my_redis=my_redis  ) ) == 0:
                    db.updateCampaigns([{'_id': thread.campaign.id, 'status': CS_COMPLETED, 'workers': 0, 'updated_at': datetime.datetime.utcnow()} for thread in done_threads])

            del done_threads[:]

        # if no accounts to add and no more active threads, quit loop
        if len(threads) == 0:
            rootLogger.info("[Main]: Exit main loop")
            break

        # sleep a while to avoid too less data to update
        time.sleep(0.25)


    end_time = time.time()
    time_delta = end_time - start_time

    rootLogger.info(f"[Main]: All processes are finnished, processing done tasks in {datetime.timedelta(seconds=time_delta)}")

    sleep_time = sleep_minutes * 60
    rootLogger.info(f"[Main]: Sleep for {sleep_minutes} minutes and start again")

    show_malloc()
    time.sleep(sleep_time)
