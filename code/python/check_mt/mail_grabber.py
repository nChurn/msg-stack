import socket, requests, time, datetime, threading
import concurrent.futures
import binascii
import re
import traceback
import json
import urllib
import sys

# from includes.IMAP4Socks import MYIMAP4, MYIMAP4_SSL
# from includes.POP3Socks import MYPOP3, MYPOP3_SSL
from includes.ProtocolErrors import retry_list, socket_errors, auth_error_list

from includes.MailGrabberClass import POP3MailProcessor, IMAPMailProcessor, WEBMailProcessor, skip_errors
common_errors = ('EOF', '[SYS/TEMP]', '-ERR')
import includes.Database as db

from includes.RootLogger import rootLogger

# TODO: remove import as useless
import random

NEED_GRAB_YES = 1
NEED_GRAB_NO = 2
NEED_GRAB_ACTIVE = 3

MAIL_NO_BODY = 0
MAIL_MARK_TO_DOWNLOAD_BODY = 1
MAIL_HAS_BODY = 2


# get socks, make some changes
def getSocksList(socks):
    # with threadLock:
    threadLock.acquire(blocking=True, timeout=300)
    try:
        db_socks = db.getSocks(socks_type="grabber", row_as_dict=True, alive_only=True, allow_smtp_only=True, enabled_only=True)
        # mark all processes are zero
        for item in db_socks:
            item['processes'] = 0
            # try to get proxy from original list
            proxy = next( (old_item for old_item in socks if old_item['id'] == item['id']), None)
            if proxy is not None:
                item['processes'] = proxy['processes']
    except Exception as e:
        # raise e
        rootLogger.error(f"getSocksList error:{e}")
        db_socks = []
    finally:
        if threadLock.locked():
            threadLock.release()

    return db_socks

def addThread(threads, account, settings):
    # get mail dump for account
    mail_dumb = db.getLatestMailDumpForEmailAccount(account.id)
    new_thread = GrabberThread(account, prefix=f"{account.id}", dump=mail_dumb, max_mail_days_old=int(settings['max_mail_days_old']))
    new_thread.daemon = True
    new_thread.start()
    threads.append( new_thread )

    # db.updateMailccount(account.id, {'need_grab_emails': NEED_GRAB_ACTIVE})

    return threads

class GrabberThread(threading.Thread):
    def __init__(self, account, prefix='', blacklist=[], dump=None, max_mail_days_old=90):
        self.account = account
        self.prefix = prefix
        self.started_at = None
        self.blacklist = blacklist
        self.dump = dump
        self.error_attempts = 0
        self.max_mail_days_old = max_mail_days_old

        self.account_result = {
            '_id': account.id,
            'need_grab_emails': NEED_GRAB_ACTIVE,
            'all_names': account.all_names,
            'name': account.name,
            'has_errors': account.has_errors,
            'error_at': account.error_at,
            'error_log': '',
            'mail_dumps': account.mail_dumps,
            'addresses': account.addresses,
        }
        # startt regular
        threading.Thread.__init__(self)

    def run(self):
        self.started_at = datetime.datetime.utcnow()
        rootLogger.info(f"Account[{self.prefix}]: Begin grab")
        # time.sleep(random.randrange(5, 15))
        self.provideSock()

        if self.sock_data is None:
            rootLogger.info(f"Account[{self.prefix}]: no free proxy, exit for now.")
            # mark as need grab emails
            self.account_result['need_grab_emails'] = NEED_GRAB_YES
            return True

        force_ssl = False
        # check if we got web-acc
        if self.account.web_url and self.account.web_login and self.account.web_password:
            selected_processor = WEBMailProcessor
            prefix=f"Account[{self.prefix}]WEB: "
            # return True

        elif self.account.imap_alive > 0:
            # prefer to use imap over pop3
            selected_processor = IMAPMailProcessor
            prefix=f"Account[{self.prefix}]IMAP: "
            if self.account.imap_ssl > 0:
                force_ssl = True

        elif self.account.pop3_alive > 0:
            selected_processor = POP3MailProcessor
            prefix=f"Account[{self.prefix}]POP3: "
            if self.account.pop3_ssl > 0:
                force_ssl = True

        from_mail = self.getFromMail()
        all_names_list = self.account.all_names.split(',')
        today_date = datetime.datetime.utcnow()

        try:
            with selected_processor( account=self.account, socks_creds=self.sock_data, ssl_context=None, prefix=prefix) as server:
                folder_list = server.getFolders()
                msg_amount = 0
                for folder in folder_list:
                    if self.max_mail_days_old > 0:
                        headers_only = False
                    else:
                        headers_only = True
                    folder = re.sub('/\s', '', folder)
                    # rootLogger.info(f"Account[{self.prefix}]: Select folder:{folder}")
                    msg_amount = server.selectFolder(folder)
                    # skip all empty folders
                    if msg_amount == 0:
                        continue

                    rootLogger.info(f"Account[{self.prefix}]: Folder[{folder}] has {msg_amount} messages")
                    # go in reverse order
                    for msg_num in range(msg_amount, 0, -1):
                        try:
                            message = server.getMessage(msg_num, headers_only)
                        except Exception as e:
                            if self.msgErrorServerRelated(e):
                                self.account_result['error_log'] = ''
                                raise e

                            rootLogger.error(f"Account[{self.prefix}]: Error processing: {traceback.format_exc()}")
                            self.account_result['error_log'] += f"\nmsg_num[{msg_num}]:{e}\n"
                            continue

                        # rootLogger.info(f"Got message data")
                        mail_record = self.processEmailData(message, msg_num, server, folder, self.dump)

                        # stop download earlier data if it's allready been grabbed earlier
                        if self.dump is not None and (self.dump.fp_crc == mail_record['fp_crc'] or self.dump.mail_date > mail_record['mail_date']):
                            rootLogger.info(f"Account[{self.prefix}]: Found mail that allready got, stop any processings in this folder: crc:{self.dump.fp_crc == mail_record['fp_crc']} date:{self.dump.mail_date > mail_record['mail_date']}")
                            break

                        mandatory = ('from', 'to')
                        no_mandatory = False
                        for hdr in mandatory:
                            if len(mail_record[hdr]) == 0:
                                rootLogger.info(f"Account[{self.prefix}]: Skip mail[{msg_num}] processing: {hdr} is missing")
                                no_mandatory = True
                                break

                        if no_mandatory:
                            continue

                        # process headers_only flag:
                        date_dif = today_date - mail_record['mail_date']
                        if headers_only is False and date_dif.days > self.max_mail_days_old:
                            headers_only = True
                            rootLogger.info(f"Account[{self.prefix}]: date_dif.days:{date_dif.days}>{self.max_mail_days_old} - switch to load headers only")
                        else:
                            pass

                        # put mail results
                        # with threadLock:
                        threadLock.acquire(blocking=True, timeout=300)
                        try:
                            results.append(mail_record)
                        except Exception as e:
                            # raise e
                            rootLogger.error(f"Account[{self.prefix}]: error appending result:{e}")
                        finally:
                            if threadLock.locked():
                                threadLock.release()

                        # increase counter
                        self.account_result['mail_dumps'] += 1

                        # list of {'holder': 'holder name', 'mail': 'abc@zyx.com'} records
                        extracted_addresses = server.extractEmails(message)

                        # process all extracted adresses to remove account plus make them unique
                        login_item = next( (item for item in extracted_addresses if from_mail in item['mail']), None)
                        if login_item is not None and len(login_item['holder']) > 0 and login_item['holder'] not in login_item['mail']:
                            all_names_list.append(login_item['holder'])
                            if self.account.auto_update_name == 1:
                                self.account_result['name'] = login_item['holder']
                            else:
                                pass
                                # rootLogger.info(f"Account[{self.prefix}]: Skip updating holder's name, reason: name was updated via GUI")

                        # remove all non unique names from result
                        all_names_list = list(set(all_names_list))

                        # make names in one big string
                        self.account_result['all_names'] = ",".join(all_names_list)

                        # making list of contact emails unique plus remove task login
                        addressbook = []
                        for item in extracted_addresses:
                            if from_mail not in item['mail']:
                                addressbook.append({
                                    'email_account_id': self.account.id,
                                    'address': item['mail'],
                                    'name': item['holder']
                                })

                        # with threadLock:
                        threadLock.acquire(blocking=True, timeout=300)
                        try:
                            addresses.extend(addressbook)
                        except Exception as e:
                            # raise e
                            rootLogger.error(f"Account[{self.prefix}]: error extend addressbook:{e}")
                        finally:
                            if threadLock.locked():
                                threadLock.release()

                        # make sleep in this loop just to ensure that main thread has a time window to access data
                        time.sleep(0.125)

        except Exception as e:
            self.account_result['error_log'] += f"\nDownload error:{traceback.format_exc()}"

            # make small processing of errors
            for s_error in socket_errors:
                if s_error.lower() in self.account_result['error_log'].lower():
                    rootLogger.info(f"Account[{self.prefix}]: Process error: socket related error:{e}")
                    self.error_attempts += 1
                    if self.error_attempts < self.max_error_attempts:
                        self.provideSock()
                        if self.sock_data is None:
                            rootLogger.info(f"Account[{self.prefix}]: no free proxy, exit for now.")
                            # mark as need grab emails
                            self.account_result['need_grab_emails'] = 1
                    else:
                        rootLogger.info(f"Account[{self.prefix}]: Process error: exceeds maximum attempts stop processing")

            # check variants when something is might be retried
            # if ctx is None and not force_ssl:
            if force_ssl:
                for err_var in retry_list:
                    if err_var.lower() in self.account_result['error_log'].lower():
                        rootLogger.info(f"Account[{self.prefix}]: Process error: ip/blacklist related error:{e}")

                        if self.error_attempts < self.max_error_attempts:
                            self.provideSock()
                            if self.sock_data is None:
                                rootLogger.info(f"Account[{self.prefix}]: no free proxy, exit for now.")
                                # mark as need grab emails
                                self.account_result['need_grab_emails'] = 1
                        else:
                            rootLogger.info(f"Account[{self.prefix}]: Process error: exceeds maximum attempts stop processing")

            # raise e
            rootLogger.info(f"Account[{self.prefix}]: Process error:{str(e)}")
            self.account_result['has_errors'] = 1

        all_names_list = [name for name in all_names_list if len(name) > 0]
        self.account_result.update({
            'all_names': ",".join(all_names_list),
            'need_grab_emails': NEED_GRAB_NO,
            'error_at': datetime.datetime.utcnow() if self.account_result['has_errors'] == 1 else self.account.error_at
        })

        self.freeSock()
        # done
        return True

    def processEmailData(self, message, msg_num, server, folder='', mail_dump=None):
        # process body
        has_attaches = 0
        save_files = False
        (body, attachments) = server.getMailBody(message)

        # if returned attachements info
        if len(attachments) > 0:
            has_attaches = 2

        # process headers
        headers_dict = server.getMailHeaders(message)
        headers_json = json.dumps(headers_dict)

        # date
        mdt = server.getMailDateTime(headers_dict, mail_dump)
        # has attaches
        if 'Content-Type' in headers_dict and has_attaches == 0:
            has_attaches = 1

        return {
            "mail_account_id": self.account.id,
            "msg_num": msg_num,
            "from": headers_dict['From'],
            "to": headers_dict["To"],
            "subject": headers_dict['Subject'],
            "mail_date": mdt,
            "body":body,
            "headers": headers_json,
            "has_attaches": has_attaches,
            "attach_path": json.dumps(attachments),
            "is_spam": self.checkForSpam(body),
            # append folder value to this item
            "folder_path": folder,
            "fp_crc" :str(binascii.crc32(folder.encode('utf8')))

        }

    def provideSock(self):
        proxy = None

        # with threadLock:
        threadLock.acquire(blocking=True, timeout=300)
        try:
            # for sock in socks:
            for sock in sorted(socks, key=lambda k: k['processes'], reverse=False):
                if sock['processes'] < int(settings['process_per_proxy']) and sock['id'] not in self.blacklist:
                    # rootLogger.info(f"Account[{self.account.id}] provideSock process before apply:{sock['processes']}")
                    # easy hack for web accounts: their socks are same
                    # if web_acc and int(sock['port']) != 1550:
                    #     continue
                    sock['processes'] += 1
                    proxy = sock
                    break
                    # rootLogger.info(f"Account[{self.account.id}] provideSock process after apply:{sock['processes']}")
        except Exception as e:
            # raise e
            rootLogger.error(f"Account[{self.prefix}]: error provideSock:{e}")
        finally:
            if threadLock.locked():
                threadLock.release()


        self.sock_data = proxy
        if self.sock_data is not None:
            self.sock_data['port'] = int(self.sock_data['port'])

    def freeSock(self):
        # remove process from proxy
        # with threadLock:
        threadLock.acquire(blocking=True, timeout=300)
        try:
            for sock in socks:
                if sock['id'] == self.sock_data['id'] and sock['processes'] > 0:
                    # rootLogger.info(f"Account[{self.account.id}] freeSock process before apply:{sock['processes']}")
                    sock['processes'] -= 1
                    # rootLogger.info(f"Account[{self.account.id}] freeSock process after apply:{sock['processes']}")
        except Exception as e:
            # raise e
            rootLogger.error(f"Account[{self.prefix}]: error freeSock:{e}")
        finally:
            if threadLock.locked():
                threadLock.release()

        return True

     # returns 1 if spam, 0 if normal

    def checkForSpam(self, html_body):
        # res = MailTextGeneratorClassInstance.isSpam(html_body)
        check_res = 1
        # do a http request for another microservice in our stack
        try:
            task = {'method': 'check', 'body': html_body}
            data = json.dumps(task)

            # Convert to String
            data = str(data)

            # Convert string to byte
            data = data.encode('utf-8')

            url = 'http://python-ml:8000'
            # self.debugLog(f"checkForSpam via url:{url}")
            # Post Method is invoked if data != None
            req =  urllib.request.Request(url, data=data)

            # Response
            resp = urllib.request.urlopen(req)

            ret_json = json.loads(resp.read().decode('utf-8'))

            # self.debugLog(f"checkForSpam return:{ret_json}")

            # return 0 only if service decided that it is not spam
            if 'answer' in ret_json and ret_json['answer'] is False:
                check_res = 0

        except Exception as e:
            rootLogger.info(f"Account[{self.prefix}] checkForSpam error:{e}, mark as spam.")
            check_res = 1

        return 1

    def msgErrorServerRelated(self, e):
        ret = False
        str_e = str(e)
        for sk in skip_errors:
            if sk in str_e and str_e.lower() not in skip_errors:
                ret = True

        return ret

    def getFromMail(self):
        if len(self.account.from_mail) > 0 and '@' in self.account.from_mail:
            return self.account.from_mail

        common_login = ''
        # for normal smtp/pop/imap accounts logis is pretty clear:
        if len(self.account.imap_login + self.account.pop3_login) > 0:
            # get login from known fields
            if len(self.account.imap_login) > 0:
                common_login = self.account.imap_login
            elif len(self.account.pop3_login) > 0:
                common_login = self.account.pop3_login
            else:
                common_login = self.account.smtp_login

            common_host = ''
            if len(self.account.imap_host) > 0:
                common_host = self.account.imap_host
            elif len(self.account.pop3_host) > 0:
                common_host = self.account.pop3_host
            else:
                common_host = self.account.smtp_host

            # check if we got some dumb fuck values instead of @ => #, %,+
            match = re.search(r'\S+(\#|\%|\+)\S+\.\S+', common_login)
            if match is not None:
                common_login = re.sub(r'(\#|\%|\+)', '@', common_login)

            if "@" not in common_login:
                # remove shit like smtp(2).
                splitted = re.split(r'(smtp(\d+)?\.|pop(\d+)?\.|imap(\d+)?\.)', common_host)
                if len(splitted) > 0:
                    # save only 2nd level domain
                    spl = splitted[-1]
                    if len( spl ) > 1:
                        spl2 = ".".join(spl.split('.')[-2:])
                    else:
                        spl2 = spl[0]
                    common_login = f"{common_login}@{spl2}"
                else:
                    common_login = f"{common_login}@{common_host}"
        elif len(self.account.web_login) > 0:
            # common case: login @ 2nd-level host
            url = ".".join( self.account.web_login.split('/owa')[0].split('.')[1:] )
            common_login = f"{self.account.web_login}@{url}"

        return common_login

threadLock = threading.Lock()

socks = []
accounts = []
# will contain mail-dumps
results = []
# will contain addressbook data for every account
addresses = []
settings = {}

if __name__ == "__main__":
    sleep_minutes = 5
    start_time = time.time()
    rootLogger.info("Begin")

    # socks check interval
    sci = 300
    last_check = time.time()

    # get all socks for grabbing
    socks = []
    try:
        socks = getSocksList([])
    except Exception as e:
        # raise e
        rootLogger.error(f"getSocksList:{e}")
        rootLogger.info(f"Sleep for 5 minutes and try again")
        time.sleep(5*60)
        sys.exit(0)

    # get system settings
    try:
        settings = db.getSystemSettings()['mail_grabber']
        rootLogger.info(f"System settings: {settings}")
    except Exception as e:
        rootLogger.error(f"db.getSystemSettings:{e}")
        rootLogger.info(f"Sleep for 5 minutes and try again")
        time.sleep(5*60)
        sys.exit(0)
        # raise e


    # calculate chunk size
    chunk_size = min(int(settings['number_process']), len(socks)*int(settings['process_per_proxy']))
    rootLogger.info(f"Calculated chunk size: {chunk_size}")

    # create main event loop
    threads = []
    rootLogger.info("Enter main loop")

    # get all accounts for grabbing
    accounts = db.getGrabbingAccounts()
    rootLogger.info(f"Accounts to process:{len(accounts)}")

    while True:
        # results = []

        # check some values
        now = time.time()
        if abs(now - last_check) >= sci:
            last_check = time.time()
            # with threadLock:
            try:
                threadLock.acquire(blocking=True, timeout=300)
                settings = db.getSystemSettings()['mail_grabber']
                socks = getSocksList(socks)
                accounts = db.getGrabbingAccounts()
            except Exception as e:
                # raise e
                rootLogger.error(f"Refresh settings, accounts and socks error:{e}")
            finally:
                if threadLock.locked():
                    threadLock.release()

            chunk_size = min(int(settings['number_process']), len(socks)*int(settings['process_per_proxy']))
            rootLogger.info(f"Settings refreshed, still has accounts to process:{len(accounts)}, threads processing:{len(threads)}")

        # check results for all threads
        done_accounts = []
        for idx, thread in enumerate( threads ):
            if not thread.isAlive():
                rootLogger.info(f"Thread[{thread.prefix}] done.")
                # db.updateMailAccount(thread.account.id, thread.account_result)
                threads.pop(idx)
                done_accounts.append(thread.account_result)

        if len(done_accounts):
            db.updateMailAccounts(done_accounts, recalc_values=True)
            del done_accounts[:]


        # add new threads if possible
        if len(threads) < chunk_size:
            marked_accounts = []
            while len(threads) < chunk_size:

                # no reason for other actions, just exit loop
                if len(accounts) == 0:
                    rootLogger.info(f"No more accounts to check.")
                    break

                try:
                    # account = accounts.next()
                    account = accounts.pop()
                    rootLogger.info(f"Get next account: {account.id}")
                    threads = addThread(threads, account, settings)
                    marked_accounts.append({
                        '_id':account.id,
                        'need_grab_emails': NEED_GRAB_ACTIVE,
                    })
                except Exception as e:
                    # account = None
                    rootLogger.error(f"Get next account: {e}")
                    break

            if len(marked_accounts):
                db.updateMailAccounts(marked_accounts)
                del marked_accounts[:]


        # update database with account check result
        if len(results) > int(settings['partial']) or len(threads) == 0:
            #
            marked_accounts = [{'_id': thread.account_result['_id'], 'mail_dumps': thread.account_result['mail_dumps']} for thread in threads]

            # rootLogger.info(f"Update records in database because: len(results) > int(settings['partial'])({len(results) > int(settings['partial'])}) or len(threads) == 0({len(threads) == 0})")
            # with threadLock:
            threadLock.acquire(blocking=True, timeout=300)
            try:
                db.saveMailGrabberData(results, addresses, marked_accounts)
                # remove all data so threads will refill it once again
                del results[:]
                del addresses[:]
                # results = []
                # addresses = []
                del marked_accounts[:]
            except Exception as e:
                # raise e
                rootLogger.error(f"saveMailGrabberData error:{e}")
            finally:
                if threadLock.locked():
                    threadLock.release()

        # if no accounts to add and no more active threads, quit loop
        if len(threads) == 0:
            rootLogger.info("Exit main loop")
            break

        # sleep a while to avoid too less data to update
        time.sleep(0.25)


    end_time = time.time()
    time_delta = end_time - start_time

    rootLogger.info(f"All processes are finnished, processing done tasks in {datetime.timedelta(seconds=time_delta)}")

    sleep_time = sleep_minutes * 60
    rootLogger.info(f"Sleep for {sleep_minutes} minutes and start again")
    time.sleep(sleep_time)
