from includes.RootLogger import rootLogger
import traceback
import datetime
import concurrent.futures
import time
import threading
import re
import json

from includes.SMTPSocks import MYSMTP, MYSMTP_SSL, retry_list, socket_errors, auth_error_list, force_ssl_list, wrong_ssl_list, send_limit_list
from includes.MailAnswerClass import MailAnswerClass
from webmails.WebMailClass import WebMailClass
import urllib.request, urllib.parse, urllib.error

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate, formataddr, parseaddr
from email.header import Header
# price overrider
import decimal, random, string
import requests

from includes.congrats import congrats, congrat_subjs

# read data from .env file
import os
from os.path import join, dirname
from dotenv import load_dotenv
# Create .env file path.
dotenv_path = join(dirname(__file__), '.env')
# Load file from the path.
load_dotenv(dotenv_path)

from pathlib import Path

re_char_enc = re.compile(r'^\=\?[a-z0-9\-_]{4,24}\?.+\?\=$', re.IGNORECASE)

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

# error types
ERR_NO = 0
ERR_RETRY = 1
ERR_SOCKET = 2
ERR_AUTH = 3
ERR_NON_MARK = 4
ERR_EXCEED = 5

# just for ease of debug
def itemLight(dict_item, restricted=('attachements', 'some_field', 'macro_tpls')):
    return {k:v for k, v in dict_item.items() if k not in restricted}



class SMTPThread(threading.Thread):
    # macros related vars
    current_letter = 1
    change_sequence_items = {}

    # some servers reject any connection due to...whatever, so try
    socket_error_counter = 0
    max_socket_errors = 25

    # debug related variables
    sleep_time = 0.25
    sleep_time_delta = 1.25

    # save login timestamp for better calculations
    last_login = time.time()
    last_message = 0
    extra_sleep = 15 #extra seconds to sleep when we reach send mail limits

    # TODO: make all debug vars via .env file
    # when True - sending will be emulated via sleep
    skip_send = True if os.getenv('SKIP_SEND') == 'True' else False
    # when True - we will show real body and not [body]
    show_body_on_skip = True if os.getenv('SKIP_SEND_SHOW_BODY') == 'True' else False
    # when True - mail well be logged as string
    show_raw_on_skip = True if os.getenv('SKIP_SEND_SHOW_RAW') == 'True' else False
    # different behaviour for emulating send
    emulate_error_retry = True if os.getenv('EMULATE_RETRY') == 'True' else False
    emulate_error_socket = True if os.getenv('EMULATE_SOCKET') == 'True' else False
    emulate_error_auth = True if os.getenv('EMULATE_AUTH') == 'True' else False
    emulate_error_non_mark = True if os.getenv('EMULATE_NON_MARK') == 'True' else False

    # when True - will always use debug proxy instead of trying to get from database
    use_debug_proxy = True if os.getenv('USE_DEBUG_PROXY') == 'True' else False
    debug_proxy = {"host":"142.234.157.99", "port":4524, "login":"", "password":"", "hostname":"test.hostname.com"}

    # when True, use list below as to_mail
    send_test = True if os.getenv('SEND_TEST') == 'True' else False
    # test_mails = ['tstchld11@wp.pl','tstchld12@wp.pl','tstchld21@onet.pl','tstchld21@eclipso.eu','tstchld22@eclipso.eu']
    # test_mails = ['tstchld11@wp.pl','tstchld12@wp.pl','tstchld13@wp.pl','tstchld14@wp.pl','tstchld21@eclipso.eu','tstchld22@eclipso.eu','tstchld23@eclipso.eu','tstchld11@eclipso.eu']
    test_mails = ['paniwom124@tjuln.com']
    test_dl_links = []

    def __init__(self, campaign, account, socks=[], settings=None, my_redis=None, threadLock=None, attachements=[], macro_tpls=[]):
        self.campaign = campaign
        self.account = account
        self.started_at = None
        self.socks = socks
        self.settings = settings
        self.my_redis = my_redis
        self.threadLock = threadLock
        self.attachements = attachements
        self.macro_tpls = macro_tpls

        self.blacklist = []

        self.prefix = f"Account[{self.account.id}]:"

        self.force_stop = False

        self.dl_links = []

        self.max_provide_sock_attempts = 10
        self.sock_data = None

        # initialize dl links
        if os.getenv('FORCE_DL_LINKS') and len(os.getenv('FORCE_DL_LINKS')) > 10:
            self.test_dl_links = [{'url':item, 'time': datetime.datetime.utcnow()} for item in os.getenv('FORCE_DL_LINKS').split('<==>')]

        # startt regular
        threading.Thread.__init__(self)

    def run(self):
        rootLogger.info(f"{self.prefix} Begin send, skip_send:{self.skip_send}")

        # get message from redis, to avoid useless connections and socket shitting
        record = self.getAccountRecord()
        if record is None:
            rootLogger.info(f"{self.prefix}[run] no record for account, quit.")
            return True

        # check if account is dead
        if self.account.smtp_alive < 1:
            rootLogger.warning(f"{self.prefix} got account:{self.account.id} seems to be dead, quit")
            self.task = record
            self.processAuthError()
            return True

        # attempt = 0
        # while attempt < self.max_provide_sock_attempts:
        #     attempt += 1
        #     self.provideSock()
        #     if self.sock_data is None:
        #         rootLogger.error(f"{self.prefix}[run] no socket for connection, attempt:{attempt}, sleep for 5 secs.")
        #         time.sleep(5)
        #     else:
        #         break

        self.provideSock()
        if self.sock_data is None:
            rootLogger.error(f"{self.prefix}[run] no socket for connection, try again later.")
            return True

        server = self.provideServer()

        # stop any actions if can't get server
        if server is None and not self.skip_send:
            # free sock just in case
            self.freeSock()
            return True

        # get message from redis
        # record = self.getAccountRecord()

        sleep_time = 0

        reget_links = 500
        get_links_counter = 0

        # when all preparations are done, provide us with dl_links
        self.getDlLinks()
        while not self.force_stop and record is not None:
            sleep_time = 0
            # TODO: actually it's a bit overwhelmed, but it's easier to copy-past old code than to write down and test a new one
            # generate task for sending
            start_time = time.time()
            self.task = self.generateTask(record)
            # rootLogger.info(f"{self.prefix} generateTask is done:{self.task}")
            if self.task is not None:
                # rootLogger.info(f"{self.prefix} generated task:\r\n{itemLight(self.task)}\r\nfrom record:\r\n{itemLight(record)}")

                # prepares task with macross processing etc
                try:
                    self.prepareTaskForSend()
                except Exception as e:
                    # raise e
                    try:
                        self.task['record_status'] = RS_SKIPPED
                        self.task['record_status_txt'] = traceback.format_exc()
                        self.updateCampaignRecord( self.task )
                    except Exception as e2:
                        rootLogger.error(f"{self.prefix} prepare task updateCampaignRecord:'{e2}'" + "\n" + traceback.format_exc())

                    rootLogger.error(f"{self.prefix} skip prepare task:'{e}'" + "\n" + traceback.format_exc())
                    continue


                # rootLogger.info(f"{self.prefix} prepared task:\r\n{itemLight(self.task)}")

                # generate MIME email object for sending
                msg = self.generateMessageForSend()

                # send message
                send_res = self.sendMessage(msg, server)

                # process results
                if send_res['status'] == RS_NEW:
                    # if something went wrong with server connection during send
                    record['record_status'] = send_res['status']
                    break

                elif send_res['status'] != RS_SUCCESS:
                    err_type = self.getErrorType(send_res['msg'])

                    if err_type == ERR_AUTH:
                        self.processAuthError()
                        break
                    elif err_type == ERR_SOCKET:
                        if self.socket_error_counter >= self.max_socket_errors or len(self.blacklist) > self.max_socket_errors:
                            rootLogger.error(f"{self.prefix}[run][sending message][{record['id']}] max_socket_errors exceeded, process as auth error.")
                            record['record_status'] = RS_NEW
                            self.processAuthError()
                            break

                        if self.sock_data:
                            self.blacklist.append( self.sock_data['id'] )
                            self.socket_error_counter += 1

                        self.freeSock()
                        self.provideSock()
                        if self.sock_data is None:
                            rootLogger.error(f"{self.prefix}[run][sending message][{record['id']}] no socket for connection, what do we do?")
                            # break all execution for a better day
                            return True
                            send_res['status'] = RS_SKIPPED
                        else:
                            # self.socket_error_counter += 1
                            server, error = self.login()
                    elif err_type == ERR_EXCEED:
                        # sleep for 1 hour and try again a bit later...
                        self.logout(server, ' ERR_EXCEED')
                        now = time.time()

                        # sleep but keep an eye on campaign status
                        while now - self.last_login < 60*60:
                            if not self.force_stop:
                                time.sleep(5)
                            else:
                                break

                        server = self.provideServer()

                        if server is None and not self.skip_send:
                            rootLogger.error(f"{self.prefix} Can't relogin after ERR_EXCEED sleep, quit.")
                            self.force_stop = True

                    else:
                        msg = ''
                        if 'msg' in send_res:
                            msg = send_res['msg']

                        rootLogger.info(f"{self.prefix}[run][sending message][{record['id']}] unexpected shit '{msg}', mark as RS_SKIPPED, continue with next message")
                        send_res['status'] = RS_SKIPPED
                else:
                    rootLogger.info(f"{self.prefix}[run][sending message][{record['id']}] send ok, continue with next message")

                    self.last_message += 1
                    # check is we exceed max items per time:
                    if self.campaign.max_messages > 0:
                        now = time.time()
                        time_delta = now - self.last_login

                        if time_delta < self.campaign.per_time and self.campaign.max_messages <= self.last_message:
                            self.logout(server, ' max_messages')
                            self.last_message = 0
                            sleep_time = int(self.campaign.per_time - time_delta + self.extra_sleep)

                record['record_status'] = send_res['status']
                record['record_status_txt'] = send_res['msg'] + "\r\n" + send_res['full_log']
            else:
                rootLogger.info(f"{self.prefix} Empty task from record:{record}, skip sending message")
                record['record_status'] = RS_SKIPPED
                record['record_status_txt'] = "Can't create task from record."

            # save updated record data
            self.updateCampaignRecord(record)

            get_links_counter += 1
            if get_links_counter > reget_links:
                get_links_counter = 0
                self.getDlLinks()

            # check if we need to sleep a while before sending next message
            if sleep_time > 0:

                rootLogger.info(f"{self.prefix} max_messages({self.campaign.max_messages}) per time({self.campaign.per_time}) exceed, sleep for:{sleep_time} seconds.")
                time.sleep( sleep_time )
                # just in case
                sleep_time = 0
                server = self.provideServer()

                if server is None:
                    rootLogger.error(f"{self.prefix} Can't relogin after max_messages sleep, quit.")
                    self.force_stop = True


            # rootLogger.info(f"{self.prefix}:updated campaign record {record['id']} --> {record['record_status']}")

            # if all is ok, get next message
            if not self.force_stop:
                record = self.getAccountRecord()
            # rootLogger.info(f"{self.prefix}[run][sending message] next record:{record}")

            end_time = time.time()
            # rootLogger.info(f"{self.prefix} main loop one iteration:{end_time - start_time} secs")

        rootLogger.info(f"{self.prefix} we are out of main loop")

        if record is None:
            rootLogger.info(f"{self.prefix} all records processed, quit.")
        elif self.force_stop:
            rootLogger.info(f"{self.prefix} got force_stop signal, stop records processing.")


        try:
            self.logout(server)
        except Exception as e:
            pass

        # free sock before exit
        self.freeSock()
        # self.status = CS_COMPLETED

        return True

    def stop(self):
        """Force thread to sop and not send any messages since"""
        self.force_stop = True

    def isWebAcc(self):
        if self.account.web_url and self.account.web_login and self.account.web_password:
            return True

        return False

    def login(self):
        server = None
        error = None

        if self.sock_data is None:
            rootLogger.error(f"{self.prefix}[login] no socket for connection")
            return server, "no socket for connection"

        mail_host = self.account.smtp_host
        mail_port = self.account.smtp_port
        mail_user = self.account.smtp_login
        mail_password = self.account.smtp_password

        socks_creds = {
            'host': self.sock_data['host'],
            'port': int(self.sock_data['port']),
            'user': self.sock_data['login'],
            'password': self.sock_data['password']
        }

        try:
            if self.isWebAcc():
                # server = None
                mail_host = self.account.web_url
                mail_user = self.account.web_login
                mail_password = self.account.web_password

                # very important: if web acc - no passwords are allowed...
                rootLogger.info(f"{self.prefix} WebMailClass with proxy {socks_creds['host']}:{socks_creds['port']}")
                server = WebMailClass(socks_creds['host'], socks_creds['port'], webmail_url=mail_host, prefix=f"{self.prefix.replace(':','')}[Web]:")
                # server.StartSession(mail_user, mail_password, mail_host, False)
                # .StartSession(mail_user, mail_password, mail_host, False)


            elif self.account.smtp_ssl == 1:
                server = MYSMTP_SSL(host=mail_host,
                                port=mail_port,
                                local_hostname=None,
                                timeout=60,
                                socks_creds=socks_creds)
            else:
                server = MYSMTP(host=mail_host,
                                port=mail_port,
                                local_hostname=None,
                                timeout=60,
                                socks_creds=socks_creds)

            server.connect(mail_host, mail_port)

            if self.account.smtp_starttls == 1:
                server.starttls()

            server.ehlo_or_helo_if_needed()
            server.login(mail_user, mail_password)
            error = None
            self.last_login = time.time()
            # rootLogger.info(f"Proxy {sock_data['host']}:{sock_data['port']} check {mail_user}:{mail_password}@{mail_host}:{mail_port} is ok")
        except Exception as e:
            rootLogger.error(f"{self.prefix}[login]:{e}")
            # rootLogger.info(f"Proxy {sock_data['host']}:{sock_data['port']} check {mail_user}:{mail_password}@{mail_host}:{mail_port} is not ok: {e}")
            # raise e
            server = None
            error = str(e)

        return server, error

    def provideServer(self):
        server = None
        error = None

        # if skip sending, no reason to connecto to server
        if self.skip_send:
            return server

        server, error = self.login()

        # process login errors
        while server is None:
            # rootLogger.info(f"{self.prefix}[run] Processing login error:{error}")
            err_type = self.getErrorType(error)
            if err_type == ERR_NO:
                rootLogger.info(f"{self.prefix}[run] login error is None. Perhaps we are in test cases? Normal behaviour goes on.")
                break
            elif err_type == ERR_SOCKET:
                if self.socket_error_counter >= self.max_socket_errors:
                    rootLogger.error(f"{self.prefix}[run] max_socket_errors exceeded, process as auth error.")
                    self.processAuthError()
                    return None

                rootLogger.info(f"{self.prefix}[run] login error is in socket. Blacklist socket and try to get new one.")

                if self.sock_data:
                    self.blacklist.append( self.sock_data['id'] )

                self.freeSock()
                self.provideSock()
                if self.sock_data is None:
                    rootLogger.error(f"{self.prefix}[run] no socket for connection, what do we do?")
                    return None
                else:
                    self.socket_error_counter += 1
                    server, error = self.login()
            elif err_type == ERR_AUTH:
                rootLogger.info(f"{self.prefix}[run] login error is in auth.")
                self.processAuthError()
                return None
            elif err_type == ERR_NON_MARK:
                rootLogger.info(f"{self.prefix}[run] login error is in non mark. Make behaviour as auth error.")
                self.processAuthError()
                return None
            else:
                rootLogger.info(f"{self.prefix}[run] login error is not expected. Make behaviour as auth error.")
                self.processAuthError()
                return None

        return server

    def logout(self, server, extra=' '):
        try:
            if server is not None:
                server.close()
        except Exception as e:
            rootLogger.error(f"{self.prefix} close server{extra}:{e}")

        self.freeSock()
        self.last_login = time.time()

    def provideSock(self):
        proxy = None

        self.threadLock.acquire(blocking=True, timeout=300)
        try:
            for sock in sorted(self.socks, key=lambda k: k['processes'], reverse=False):
                if sock['processes'] < int(self.settings['connection_per_proxy']) and sock['id'] not in self.blacklist:
                    sock['processes'] += 1
                    proxy = sock
                    # rootLogger.info(f"{self.prefix}[provideSock][{proxy['id']}]")
                    break
        except Exception as e:
            rootLogger.error(f"{self.prefix}[provideSock]:{e}")
        finally:
            if self.threadLock.locked():
                self.threadLock.release()

        self.sock_data = proxy
        if self.sock_data is not None:
            self.sock_data['port'] = int(self.sock_data['port'])

    def freeSock(self):
        if self.sock_data is None:
            return True

        # remove process from proxy
        self.threadLock.acquire(blocking=True, timeout=300)
        try:
            for sock in self.socks:
                if sock['id'] == self.sock_data['id'] and sock['processes'] > 0:
                    sock['processes'] -= 1
                    # rootLogger.info(f"{self.prefix}[freeSock][{self.sock_data['id']}]")
                    self.sock_data = None
                    break
        except Exception as e:
            rootLogger.error(f"{self.prefix}[freeSock]:{e}")
        finally:
            if self.threadLock.locked():
                self.threadLock.release()

        return True

    def getErrorType(self, _error):
        # just in case of
        error = f"{_error}"

        if _error is None or error == "None" or error == "":
            return ERR_NO

        # i guess it is proxy error
        # if "Errno 111" in error or "no socket for connection" in error or 'Connection closed unexpectedly' in error or 'Connection reset by peer' in error or 'timed out' in error:
        #     return ERR_SOCKET

        for record in retry_list:
            if error in record:
                return ERR_RETRY

        for record in auth_error_list:
            if error in record:
                return ERR_AUTH

        for record in socket_errors:
            if error in record:
                return ERR_SOCKET

        for record in send_limit_list:
            if error in record:
                return ERR_EXCEED

        return ERR_NON_MARK

    # processes common behaviour for any auth related errors
    def processAuthError(self):
        self.freeSock()
        # rootLogger.info(f"{self.prefix} Stop futher work, ignore mark all records.")
        # return True

        try:
            if self.campaign.fail_behaviour == 0:
                rootLogger.info(f"{self.prefix} Stop futher work, mark all records as fail")
                self.changeAccountRecordsStatus(old_status=RS_PROCESSING, new_status=RS_FAILED)
                self.changeAccountRecordsStatus(old_status=RS_NEW, new_status=RS_FAILED)

                # mark current record as well
                if self.task is not None and 'id' in self.task:
                    self.task['record_status'] = RS_FAILED
                    self.task['record_status_txt'] = 'Marked as failed due to campaign settings.'
                    self.updateCampaignRecord(self.task)

            elif self.campaign.fail_behaviour == 1:
                rootLogger.info(f"{self.prefix} Stop futher work, mark all records as free for all")
                self.changeAccountRecordsStatus(old_status=RS_PROCESSING, new_status=RS_NEW)
                self.moveCampaignRecords(old_mac=self.account.id, new_mac='none')

                # mark current record as well
                if self.task is not None and 'id' in self.task:
                    self.task['record_status'] = RS_NEW
                    self.task['mail_account_id'] = ''
                    self.task['record_status_txt'] = ''
                    self.updateCampaignRecord(self.task)


        except Exception as e:
            rootLogger.error(f"{self.prefix}[processAuthError]:{e}")
            # raise e

    # generates random string
    def randomString(self, size_min, size_max=0, chars=string.ascii_letters + string.digits):
        if size_max == 0:
            gen_size = size_min
        else:
            gen_size = random.randint(size_min, size_max)

        return ''.join(random.choice(chars) for _ in range(gen_size))

    # process all macroses on string one by one
    def processMacrosses(self, string, task, allow_change_repl=True):
        # first of all, replace any macro templates with their respective content
        # for key in task['macro_tpls']:
        for key in self.macro_tpls:
            while key in string:
                # rootLogger.info(f"{self.prefix} found macro[{}] in [{}]".format(key, string))
                # repl_content is randomly chosen string from multiple strings
                repl_content = random.choice(self.macro_tpls[key].split('\n'))
                # rootLogger.info(f"{self.prefix} replace macro[{}] with [{}]".format(key, repl_content))
                string = string.replace(key, repl_content)

        # process common
        # string = re.sub(r'\[\%\%ACCOUNTNAME\%\%\]', task['account_name'], string, flags=re.IGNORECASE | re.MULTILINE )
        # sometimes this causes a lot of errors on empty strings
        if "\[\%\%FROMNAME\%\%\]" in string:
            string = re.sub(r'\[\%\%FROMNAME\%\%\]', task['from_name'], string, flags=re.IGNORECASE | re.MULTILINE )

        if "\[\%\%TONAME\%\%\]" in string:
            string = re.sub(r'\[\%\%TONAME\%\%\]', task['to_name'], string, flags=re.IGNORECASE | re.MULTILINE )

        # string = re.sub(r'\[\%\%FROMEMAIL\%\%\]', task['smtp_login'], string, flags=re.IGNORECASE | re.MULTILINE )
        string = re.sub(r'\[\%\%FROME?MAIL\%\%\]', task['from_mail'], string, flags=re.IGNORECASE | re.MULTILINE )
        string = re.sub(r'\[\%\%TOE?MAIL\%\%\]', task['address'], string, flags=re.IGNORECASE | re.MULTILINE )

        string = re.sub(r'\[\%\%ACCORIGNAME\%\%\]', task['from_name_orig'], string, flags=re.IGNORECASE | re.MULTILINE )
        string = re.sub(r'\[\%\%ACCORIGMAIL\%\%\]', task['from_mail_orig'], string, flags=re.IGNORECASE | re.MULTILINE )

        #
        string = re.sub(r'\[\%\%FROME?MAILDOMAIN\%\%\]', task['from_mail'].split('@')[-1], string, flags=re.IGNORECASE | re.MULTILINE )

        # process pseudorandom
        price = str(decimal.Decimal(random.randrange(9100, 95099))/100)
        rand_str = self.randomString(24)
        string = re.sub(r'\[\%\%PRICE\%\%\]', price, string, flags=re.IGNORECASE | re.MULTILINE )
        string = re.sub(r'\[\%\%RANDSTR\%\%\]', rand_str, string, flags=re.IGNORECASE | re.MULTILINE )
        # process complex macros handling
        string = self.megaMacrosReplace(string, allow_change_repl)
        # process list choise
        string = self.macrosMultiOptionReplace(string, allow_change_repl)

        # rootLogger.info(f"{self.prefix} processMacrosses string result:{}".format(string))
        return string

    # process macros with random selection of multiple items
    def macrosMultiOptionReplace(self, my_string, allow_change_repl=True):
        # pattern = re.compile("(?:\[\%\%)(.+?)(?:\%\%\])", flags=re.IGNORECASE | re.MULTILINE )
        pattern = re.compile("(\[\%\%)(.+?)(\%(\(?const\)?)?\%\])", flags=re.IGNORECASE | re.MULTILINE )

        # process every pattern, if it has Const = generate one constant and replace everywhere, if not = replace with random
        search_res = pattern.findall(my_string)
        # print(search_res)
        search_res_unique = list(dict.fromkeys(search_res))
        # print(search_res_unique)
        # TODO: make CONST == const == Const == cOnst == etc

        for item in search_res_unique:
            repl_pattern = "".join(item[:3])
            if item[3].lower() == 'const':

                if  allow_change_repl or repl_pattern not in self.change_sequence_items:
                    # rootLogger.info(f"{self.prefix} time to change repl for pattern: %s" % repl_pattern)
                    strings = item[1].split("|")
                    repl = random.choice(strings)
                    self.change_sequence_items[repl_pattern] = repl
                else:
                    # rootLogger.info(f"{self.prefix} get repl for macro: %s" % repl_pattern)
                    repl = self.change_sequence_items[repl_pattern]

                my_string = my_string.replace(repl_pattern, repl)
            else:
                # print("we got pattern with always random:")
                # print(item)
                while repl_pattern in my_string:
                    strings = item[1].split("|")
                    repl = random.choice(strings)

                    my_string = my_string.replace(repl_pattern, repl, 1)

        return my_string

    # process RandStr macro
    def megaMacrosReplace(self, my_string, allow_change_repl=True):
        # global self.current_letter
        # global self.change_sequence_items
        pattern = re.compile("(\[\%ORandStr\%)(.+?)(\%(\(?const\)?)?\%\])", flags=re.IGNORECASE | re.MULTILINE)

        # process every pattern, if it has Const = generate one constant and replace everywhere, if not = replace with random
        search_res = pattern.findall(my_string)
        # print(search_res)
        search_res_unique = list(dict.fromkeys(search_res))

        choose_str = 'abcdefghijklmnopqrstuvwxyz0123456789'
        choose_str_rev = '0123456789abcdefghijklmnopqrstuvwxyz'

        # and here we got some complexity
        for item in search_res_unique:
            repl_pattern = "".join(item[:3])
            # rootLogger.info(item)

            # process every pattern
            (size, alphabet, letter_case, change_sequence, const) = (None, None, None, 0, False)
            splitted = item[1].split(',')
            if len(splitted) > 0: size = splitted[0]
            if len(splitted) > 1: alphabet = splitted[1]
            if len(splitted) > 2: letter_case = splitted[2]
            if len(splitted) > 3: change_sequence = int(splitted[3])

            # macros string size and alphabet
            (size_min, size_max) = (int(item) for item in size.split('-'))
            # rootLogger.info(size_min, size_max)
            (alpha_min, alpha_max) = (item for item in alphabet.lower().split('-'))
            # rootLogger.info(alpha_min, alpha_max)

            if alpha_min.isdigit() and not alpha_max.isdigit():
                # support for 0-f
                chars = choose_str_rev[choose_str_rev.index(alpha_min):choose_str_rev.index(alpha_max)+1]
            else:
                # support for f-0
                chars = choose_str[choose_str.index(alpha_min):choose_str.index(alpha_max)+1]

            if letter_case == 'U':
                chars = chars.upper()
            elif letter_case == 'L':
                pass
            elif letter_case == 'LU' or letter_case == 'UL':
                # rootLogger.info(f"{self.prefix} All U or L random choise")
                if random.randint(1,101) > 50:
                    chars = chars.upper()
            elif letter_case == 'R' or letter_case is None:
                # rootLogger.info(f"{self.prefix} random every letter")
                chars += chars.upper()
                # remove non unique
                chars = "".join(set(chars))

            chars = "".join(sorted(chars))

            # is macros const
            if item[3].lower() == 'const':
                # rootLogger.info(f"{self.prefix} Const")
                const = True

            repl = self.randomString(size_min, size_max, chars)

            if const:
                # work with change sequence if it is >0
                if change_sequence > 0:
                    # time to change item or it is not exists
                    # and if it is allowed
                    if self.current_letter % change_sequence == 1 and allow_change_repl or repl_pattern not in self.change_sequence_items:
                        # rootLogger.info(f"{self.prefix} time to change repl for pattern: %s" % repl_pattern)
                        repl = self.randomString(size_min, size_max, chars)
                        self.change_sequence_items[repl_pattern] = repl
                    else:
                        # rootLogger.info(f"{self.prefix} get repl for macro: %s" % repl_pattern)
                        repl = self.change_sequence_items[repl_pattern]

                my_string = my_string.replace(repl_pattern, repl)


            else:
                while repl_pattern in my_string:
                    strings = item[1].split("|")
                    my_string = my_string.replace(repl_pattern, repl, 1)
                    repl = self.randomString(size_min, size_max, chars)

        return my_string

    # create MIME object from task data
    def generateMessageForSend(self):
        send_from = self.task['send_from']
        send_to = self.task['send_to']
        subject = self.task['subject']
        body = self.task['body']
        is_html = self.task['is_html']
        files = self.task['attachements']
        headers = self.task['headers']
        smtp_host = self.task['smtp_host']
        smtp_port = self.task['smtp_port']
        smtp_user = self.task['smtp_login']
        smtp_password = self.task['smtp_password']
        address = self.task['address']

        filename = self.task['attach_name']

        dump_headers = None

        clrf = "\n"
        # rootLogger.info(f"{self.prefix}.generateMessageForSend:{clrf}reply_mode:{self.task['reply_mode']}{clrf}subject:{subject}{clrf}body:{body}{clrf}")

        # determone if reply_mode
        if self.task['reply_mode'] and int(self.task['reply_mode']) > 0:
            # rootLogger.info(f"{self.prefix} reply_mode is active")

            subject = "Re: {}".format(self.task['dump_subject'])

            # rootLogger.info(f"{self.prefix} reply_mode subject is:{subject} instead of {self.task['subject']}")
            # rootLogger.info(f"{self.prefix} type of headers is:{}".format(type(self.task['dump_headers'])))

            # headers have double escapings, get rid of them
            try:
                # dump_headers = json.loads(self.task['dump_headers'].replace('\\\\', '\\'))
                # small preparation: get rid of unescaped double quotes in values
                mystr = self.task['dump_headers']
                mystr2 = re.sub(r'\{\"', '{--my_replace--', mystr)
                mystr2 = re.sub(r'\"\}', '--my_replace--}', mystr2)
                mystr2 = re.sub(r'\"\:\s+\"', '--my_replace--: --my_replace--', mystr2)
                mystr2 = re.sub(r'\"\,\s+\"', '--my_replace--, --my_replace--', mystr2)
                mystr2 = re.sub(r'\"', "'", mystr2)
                mystr2 = mystr2.replace('--my_replace--', '"')

                mystr2 = re.sub(r'[\r\n\t]', "", mystr2)

                mystr2 = mystr2.encode('unicode_escape')

                dump_headers = json.loads(mystr2)

            except Exception as e:
                err = f"{self.prefix}[generateMessageForSend][{self.task['id']}]:'{e}' when parsing dump_headers:{self.task['dump_headers']}, skip sending"
                rootLogger.error(err)
                return {"success" : False, "msg": err, "status": RS_SKIPPED, "full_log": f"{e}"}

            reply_processor = MailAnswerClass( self.task['dump_body'], dump_headers, body )

            if reply_processor.bodyIsLikelyBase64():
                # rootLogger.info(f"{self.prefix} dump_body is likely base64, decoding")
                reply_processor.decodeBodyFromBase64()

            # if reply_processor.bodyIsLikelyHtml() is True:
            #     rootLogger.info(f"{self.prefix}[{self.task['id']}] dump_body is likely html")
            # else:
            #     rootLogger.info(f"{self.prefix}[{self.task['id']}] dump_body is likely plain text")

            # if campaign is plain text and mail dump body is html, skip
            if is_html in (0, False) and reply_processor.bodyIsLikelyHtml() is True:
                # rootLogger.info(f"{self.prefix} Skip reply. Reason: plaint text reply mode cant process html-body from mail dump %d" % md['id'])
                err = f"{self.prefix}[generateMessageForSend] plain-text reply mode can't process html-body from mail dump:{self.task['id']}"
                return {"success" : False, "msg": err, "status": RS_SKIPPED, "full_log": err}

            body = reply_processor.getProcessed( is_html )
            self.task['body_processed'] = body

        elif self.campaign.reply_mode != 0 and int(self.task['reply_mode']) == 0:
            # generate easy body
            msg_headers_dict = {'From': send_from, 'To': send_to, 'Subject': subject}
            text_processor = MailAnswerClass( self.task['dump_body'], msg_headers_dict, body )
            # rootLogger.info(f"{self.prefix} reply_mode is inactive, {self.task['dump_body']} === {msg_headers_dict} === {body}")

            body = text_processor.getProcessed( is_html, use_reply=False )
            # rootLogger.info(f"{self.prefix}[generateMessageForSend]:{clrf}reply_mode:{self.task['reply_mode']}{clrf}subject:{subject}{clrf}body:{body}{clrf}")
            self.task['body_processed'] = body
        else:
            # do nothing, all is generated allready mannually
            pass


        if self.isWebAcc():
            msg = {
                'send_to': send_to,
                'subject': subject,
                'body': body,
                'attachment': None,
                'letter_id': None
            }

            # make dirrectory for that file
            dir_path = join(dirname(__file__), f"attachements/{self.task['id'].replace(':', '-')}")
            Path(f"{dir_path}").mkdir(parents=True, exist_ok=True)

            for f in files or []:
                if len(filename) == 0:
                    filename = f['name']

                filename = filename.replace('/', '-')

                # save file somewhere
                file_path = f'{dir_path}/{filename}'
                rootLogger.info(f"{self.prefix} Attachement path:{file_path}")

                with open(file_path, 'wb') as binFile:
                    binFile.write(f['data'])

                msg.update({'attachment':{
                    # 'data': f['data'],
                    'name': filename,
                    'path': file_path,
                }})

            # check if we got special field with letter id in dump
            if dump_headers is not None and 'Outlook-Inner-Id' in dump_headers:
                msg.update({'letter_id': dump_headers['Outlook-Inner-Id']})

        else:
            msg = MIMEMultipart()
            # set to utf8 always
            msg.set_charset("utf-8")

            # add custom headers
            for key, value in headers.items():
                msg[key] = value

            msg['From'] = send_from
            # msg['To'] = COMMASPACE.join(send_to)
            msg['To'] = send_to
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = subject

            if( is_html ):
                # rootLogger.info(f"{self.prefix} Message body is html")
                msg.attach(MIMEText(body, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # attach files one by one
            for f in files or []:
                if len(filename) == 0:
                    filename = f['name']
                part = MIMEApplication(
                        f['data'],
                        # Name=f['name']
                        Name=filename
                    )
                part['Content-Disposition'] = 'attachment; filename="%s"' % filename
                msg.attach(part)

        return msg

    def taskAppendAttach(self, task):
        self.threadLock.acquire(blocking=True, timeout=300)
        try:
            # get only today attachements
            min_date = datetime.datetime.utcnow() - datetime.timedelta(hours=20)
            self.attachements = [item for item in self.attachements if item['created_at'] > min_date or item['updated_at'] > min_date]

            # sort to get less used one
            self.attachements = sorted(self.attachements, key=lambda k: k['used'], reverse=False)
            if len(self.attachements) > 0:
                task['attachements'] = [self.attachements[0]]
                self.attachements[0]['used'] += 1
            else:
                task['attachements'] = []
        except Exception as e:
            rootLogger.error(f"{self.prefix}[generateTask] apply attachements:{e}")
            return None
        finally:
            if self.threadLock.locked():
                self.threadLock.release()

    # generate task from message data
    def generateTask(self, record):
        # make duplicate
        task = dict(record)

        # task['macro_tpls'] = self.macro_tpls
        task['to_name'] = task['name']
        # add necesseary fields from campaign
        fields = ('subject', 'body', 'headers', 'is_html', 'reply_mode', 'account_name')
        for key in fields:
            task[key] = getattr(self.campaign, key)

        # small addon for new type of campaigns, where reply_mode is based on what we've found in letters for particular account-address bound
        if 'reply_mode' in record:
            task['reply_mode'] = record['reply_mode']

        if len( task['headers'] ) > 0:
            task['headers'] = json.loads(self.campaign.headers)
        else:
            task['headers'] = {}

        # add necesseary fields from mail account
        fields = ('from_name', 'from_mail', 'smtp_host', 'smtp_port', 'smtp_login', 'smtp_password', 'smtp_ssl', 'smtp_starttls')
        for key in fields:
            task[key] = getattr(self.account, key, '')
            # task[key] = worker['account'][key]

        # from name and from mail are a bit complex fields
        if(task['from_name'] == ''):
            task['from_name'] = self.account.name

        if(task['from_mail'] == ''):
            task['from_mail'] = self.account.smtp_login

        task['attach_name'] = self.campaign.attach_name

        # make default behaviour
        task['prefered_method'] = 'attach'
        task['attachements'] = []

        # skip any attaches actions
        if self.campaign.has_attaches == 0:
            task['prefered_method'] = 'link'

        # prepare for reply mode
        if self.campaign.reply_mode == 1 and 'reply_mode' not in task and ( 'dump_body' not in task or len(task['dump_body'] + task['dump_subject'] + task['dump_headers']) == 0):
            rootLogger.error(f"{self.prefix}[generateTask] Reply mode misbehaviour: task[{task['id']}] has no mail_dump data in it")
            return None

        return task

    def prepareTaskForSend(self):
        task = self.task
        # process from and to fields
        if len(task['from_name']) > 0:
            task['from_name'] = task['from_name'].strip()
            # remove any shitty chars from begin and end of string if it's not special encodings
            if re_char_enc.match(task['from_name']) is None:
                task['from_name'] = re.sub(r'(^(\W+))|((\W+)$)', '', task['from_name'])

        # save original from_name and from_mail
        task['from_name_orig'] = task['from_name']
        task['from_mail_orig'] = task['from_mail']
        # task['account_name'] = None

        # check if sending to debug mails
        if self.send_test:
            test_mail = random.choice(self.test_mails)
            rootLogger.info(f"{self.prefix}[prepareTaskForSend] send_test is activated: Sending to {test_mail} instead of {task['address']}")
            task['address'] = test_mail

        # process to_name field
        if task['to_name'] is not None and len(task['to_name']) > 0:
            task['to_name'] = task['to_name'].strip()
            # remove any shitty chars from begin and end of string
            if re_char_enc.match(task['to_name']) is None:
                task['to_name'] = re.sub(r'(^(\W+))|((\W+)$)', '', task['to_name'])

            task['send_to'] = formataddr(( task['to_name'] , task['address']), charset='utf-8')
        else:
            task['to_name'] = ''
            task['send_to'] = task['address']

        # process account_name field, after to_name because of macroses
        if task['account_name'] is not None and len(task['account_name']) > 0:
            task['account_name'] = self.processMacrosses(task['account_name'], task, True)
            # override from_name and from_mail with data parsed from account_name:
            task['from_name'], task['from_mail'] = parseaddr(task['account_name'])
            # in case if one of fields if missing, replace it with original values
            if len(task['from_name']) < 1:
                task['from_name'] = task['from_name_orig']

            if len(task['from_mail']) < 1:
                task['from_mail'] = task['from_mail_orig']

        # rootLogger.info("Macros processing leter#%d" % self.current_letter)
        fields = ('from_name', 'from_mail', 'subject', 'attach_name', 'body')
        for key in fields:
            task[key] = self.processMacrosses(task[key], task, True)

        # generate proper send from after all macroses are processed
        task['send_from'] = formataddr((task['from_name'], task['from_mail']), charset='utf-8')

        # process custom headers for macrosses
        for key, value in task['headers'].items():
            # TODO: why allow_repls turned off?
            task['headers'][key] = self.processMacrosses(value, task, False)

        # append attachements if needed
        if task['prefered_method'] != 'link':
            self.taskAppendAttach(task)

        # increase step for megaMacrosReplace here to avoid multiple increations
        self.current_letter += 1

    # send prepared message
    def sendMessage(self, msg, server):
        smtp_user = self.task['smtp_login']
        address = self.task['address']

        # check if msg is dict with fails:
        if "success" in msg and not msg['success']:
            return msg

        if self.skip_send:
            # sleep_time = random.randint(self.sleep_time - self.sleep_time_delta, self.sleep_time + self.sleep_time_delta)
            sleep_time = random.uniform(self.sleep_time, self.sleep_time_delta)

            dbg_string = f"Sending message[skip_send:{self.skip_send}, reply_mode:{self.task['reply_mode']}]:\nFrom: {msg['From']}\nTo: {msg['To']}\nSubject: {msg['Subject']}\nBody:"

            if self.show_body_on_skip:
                # dbg_string += f"\n------------\n{self.task['body']}\n------------"
                dbg_string += f"\n------------\n{self.task['body_processed']}\n------------"
            else:
                dbg_string += "[body]"

            if self.show_raw_on_skip:
                dbg_string += f"\nRAW:\n------------\n{msg.as_string()}\n------------"

            dbg_string += f"\nSend mail skip, emulate via sleep {sleep_time} seconds instead"

            rootLogger.info(dbg_string)

            # if self.show_body_on_skip:
            #     rootLogger.info("Sending message:\nFrom: {}\nTo: {}\nSubject: {}\nBody:\n------------\n{}\n------------\nRAW:\n{}\nSend mail skip, emulate via sleep {} seconds instead".format(msg['From'], msg['To'], msg['Subject'], self.task['body'], msg.as_string(), sleep_time))
            # else:
            #     rootLogger.info("Sending message:\nFrom: {}\nTo: {}\nSubject: {}\nBody:\n------------\n{}\n------------\nRAW:\n{}\nSend mail skip, emulate via sleep {} seconds instead".format(msg['From'], msg['To'], msg['Subject'], self.task['body'], '[body]', sleep_time))
            time.sleep(sleep_time)

            debug_ret = {
                "status": RS_SUCCESS,
                "msg": "Send mail debug mode: skipp real mail sending",
                "full_log":""
            }

            # try different cases
            if self.emulate_error_retry:
                debug_ret["status"] = RS_FAILED
                debug_ret["msg"] = "Some text containing error:[Try again]"
            elif self.emulate_error_auth:
                debug_ret["status"] = RS_FAILED
                debug_ret["msg"] = "Some text containing error:[exceeded the configured limit]"
            elif self.emulate_error_socket:
                debug_ret["status"] = RS_FAILED
                debug_ret["msg"] = "Some text containing error:[broken pipe]"
            elif self.emulate_error_non_mark:
                debug_ret["status"] = RS_FAILED
                debug_ret["msg"] = "Some text containing error:[Your mail is some shit, that i cant send without shame for eternety]"

            return debug_ret

        result = {
            "status": RS_SUCCESS,
            "msg": "",
            "full_log": ""
        }

        serv_log = ""
        try:
            serv_log = server.get_log()

            if self.isWebAcc():
                # process msg body according to message type:
                if self.task['is_html']:
                    msg['body'] = re.sub(r'\r?\n', '', msg['body'], flags=re.IGNORECASE | re.MULTILINE )
                    msg['body'] = msg['body'].split('<body>')[1].split('</body>')[0]
                else:
                    msg['body'] = re.sub(r'\r?\n', '<br/>', msg['body'], flags=re.IGNORECASE | re.MULTILINE )

                # web account sendings
                server.SendEmail(
                    letter_id=msg['letter_id'],
                    answer_body=msg['body'],
                    report_flag=False,
                    remove_sent_flag=True,
                    attachment=msg['attachment'],
                    subject=msg['subject'],
                    send_to=msg['send_to']
                )

                try:
                    os.remove(msg['attachment']['path'])
                except Exception as e:
                    # raise e
                    rootLogger.error(f"{self.prefix}[run][sendMessage][{record['id']}] remove file ({msg['attachment']['path']}): {e}")
            else:
                # normal smtp
                try:
                    server.sendmail(smtp_user, address, msg.as_string())
                except Exception as e:
                    # raise e
                    if 'please run connect' in str(e):
                        server = self.provideServer()
                        # stop any actions if can't get server
                        if server is None and not self.skip_send:
                            result['msg'] = f"Some error during server connection:{e}"
                            result['status'] = RS_NEW


            # rootLogger.info("{} Mail[{}] sent ok:{}".format(self.prefix, self.task['id'], serv_log))
            result['msg'] = "Mail sent ok\n"
            if len(serv_log) > 0:
                result['full_log'] = "\n".join(item for item in serv_log)
            result['status'] = RS_SUCCESS
        except Exception as e:
            # rootLogger.info("error sending email:\n{}".format(e))
            rootLogger.info("{}[{}] error sending email:\n{}".format(self.prefix, self.task['id'], traceback.format_exc()))
            result['status'] = RS_FAILED

            result['msg'] = str(e)
            if server is not None:
                result['full_log'] = "\n".join(item for item in serv_log)

        finally:
            # if server is not None:
            #     try:
            #         server.close()
            #     except Exception as e:
            #         rootLogger.info("Error sendMail close server:{}".format(e))

            # log send_test data
            if self.send_test:
                result['full_log'] = 'Send test activated, sending to:{}\n{}'.format(self.task['address'], result['full_log'])

        return result

    #
    # redis related block
    #
    def getAccountRecord(self, try_empty=True, move_from=RS_NEW, move_to=RS_PROCESSING):

        camp_id = self.campaign.id
        mac_id = self.account.id

        skey = f"campaign:{camp_id}:account:{mac_id}:records:{move_from}"
        record_id = self.my_redis.spop(skey)
        # rootLogger.info(f"{self.prefix}[getAccountRecord] record_id:{record_id} from skey:{skey}")
        # rootLogger.info(f"{self.prefix} try: {}".format(skey))

        # when empty, try none list
        if record_id is None and try_empty:
            mac_id = 'none'
            skey = f"campaign:{camp_id}:account:{mac_id}:records:{move_from}"
            record_id = self.my_redis.spop(skey)
            # rootLogger.info(f"{self.prefix}[getAccountRecord] record_id:{record_id} from skey:{skey}")

        # if empty, quit
        if record_id is None:
            return None

        # get proper data from redis
        data = self.my_redis.hgetall(record_id)
        # for ease of use
        data['id'] = record_id

        # self.my_redis.hset(record_id, "record_status", move_to)

        # # rootLogger.info(f"{self.prefix} move_from:{}, move_to:{}".format(move_from, move_to))
        # # move from one list to another
        # from_key = f"campaign:{camp_id}:records:{move_from}"
        # to_key = f"campaign:{camp_id}:records:{move_to}"
        # # rootLogger.info(f"{self.prefix} {} moved from {} to {}".format(record_id, from_key, to_key))
        # self.my_redis.lrem(from_key, 0, record_id)
        # self.my_redis.lpush(to_key, record_id)

        # # move this record to pocessings
        # from_key = f"campaign:{camp_id}:account:{mac_id}:records:{move_from}"
        # to_key = f"campaign:{camp_id}:account:{mac_id}:records:{move_to}"

        # # rootLogger.info(f"{self.prefix} smove {} {} {}".format(from_key, to_key, record_id))
        # # self.my_redis.smove(from_key, to_key, record_id)
        # self.my_redis.srem(from_key, record_id)
        # self.my_redis.sadd(to_key, record_id)

        with self.my_redis.pipeline() as pipe:

            pipe.hset(record_id, "record_status", move_to)

            # rootLogger.info(f"{self.prefix} move_from:{}, move_to:{}".format(move_from, move_to))
            # move from one list to another
            from_key = f"campaign:{camp_id}:records:{move_from}"
            to_key = f"campaign:{camp_id}:records:{move_to}"
            # rootLogger.info(f"{self.prefix} {} moved from {} to {}".format(record_id, from_key, to_key))
            # pipe.lrem(from_key, 0, record_id)
            pipe.srem(from_key, record_id)
            # pipe.lpush(to_key, record_id)
            pipe.sadd(to_key, record_id)

            # move this record to pocessings
            from_key = f"campaign:{camp_id}:account:{mac_id}:records:{move_from}"
            to_key = f"campaign:{camp_id}:account:{mac_id}:records:{move_to}"

            # rootLogger.info(f"{self.prefix} smove {} {} {}".format(from_key, to_key, record_id))
            # pipe.smove(from_key, to_key, record_id)
            # pipe.srem(from_key, record_id)
            # pipe.sadd(to_key, record_id)
            pipe.smove(from_key, to_key, record_id)

            pipe.execute()

        if not bool(data):
            rootLogger.info(f"{self.prefix}[getAccountRecord] record_id:{record_id} from skey:{skey} has no data:{bool(data)} -> {data}")
            return None

        return data

    def updateCampaignRecord(self, record):

        key = record.pop('id', None)
        if key is None:
            return None

        # rootLogger.info(f"{self.prefix} updateCampaignRecord:{record}")

        camp_id = record['campaign_id']
        mac_id = record['mail_account_id'] if len(record['mail_account_id']) > 0 else 'none'
        status = int(record['record_status'])
        # update data
        # rootLogger.info(f"{self.prefix} updateCampaignRecord:{}\n{}".format(key, record))

        # self.my_redis.hmset(key, record)
        # # remove it from all status types
        # for idx in range(10):
        #     skey = f"campaign:{camp_id}:records:{idx}"
        #     self.my_redis.lrem(skey, 0, key)
        #     skey = f"campaign:{camp_id}:account:{mac_id}:records:{idx}"
        #     self.my_redis.srem(skey, key)

        with self.my_redis.pipeline() as pipe:
            # pipe.hmset(key, record)

            # update only certain fields
            upd_val = {}
            for field in ('record_status', 'record_status_txt'):
                upd_val[field] = record[field]

            pipe.hmset(key, upd_val)

            # remove it from all status types
            for idx in range(RS_NEW, RS_BLACKLIST):
                # skip needed item
                if idx == status:
                    continue

                skey = f"campaign:{camp_id}:records:{idx}"
                # pipe.lrem(skey, 0, key)
                pipe.srem(skey, key)
                skey = f"campaign:{camp_id}:account:{mac_id}:records:{idx}"
                pipe.srem(skey, key)

            # add to proper list and account set
            skey = f"campaign:{camp_id}:records:{status}"
            # pipe.rpush(skey, key)
            pipe.sadd(skey, key)

            skey = f"campaign:{camp_id}:account:{mac_id}:records:{status}"
            pipe.sadd(skey, key)

            pipe.execute()

        return True

    # TODO: deprecated?
    def changeCampaignRecordStatus(self, old_status=RS_PROCESSING, new_status=RS_SUCCESS):
        camp_id = self.campaign.id
        old_lkey = f"campaign:{camp_id}:records:{old_status}"
        new_lkey = f"campaign:{camp_id}:records:{new_status}"


        record = self.my_redis.lpop(old_lkey)
        while record:
            # rootLogger.info(f"{self.prefix} moving record:{} from {} to {}".format(record, old_status, new_status))
            rdata = self.my_redis.hgetall(record)
            mac_id = rdata["mail_account_id"]

            old_skey = f"campaign:{camp_id}:account:{mac_id}:records:{old_status}"
            new_skey = f"campaign:{camp_id}:account:{mac_id}:records:{new_status}"

            # update record data for account
            self.my_redis.hset(record, 'record_status', new_status)
            # self.my_redis.sadd(new_skey, record)
            # self.my_redis.srem(old_skey, record)
            self.my_redis.smove(old_skey, new_skey, record)

            # self.my_redis.smove(old_skey, new_skey, record)
            # rootLogger.info(f"{self.prefix} smove {} {} {}".format(old_skey, new_skey, record))

            # self.my_redis.lrem(old_lkey, 0, record)
            self.my_redis.srem(old_lkey, record)
            # rootLogger.info(f"{self.prefix} lrem {} {} {}".format(old_lkey, 0, record))

            # self.my_redis.lrem(new_lkey, 0, record)
            self.my_redis.srem(new_lkey, record)
            # rootLogger.info(f"{self.prefix} lrem {} {} {}".format(new_lkey, 0, record))

            # self.my_redis.rpush(new_lkey, record)
            self.my_redis.sadd(new_lkey, record)
            # rootLogger.info(f"{self.prefix} rpush {} {}".format(new_lkey, record))

            # get new record from database
            record = self.my_redis.lpop(old_lkey)

    def moveCampaignRecords(self, old_mac, new_mac, status=RS_NEW, records=[]):
        camp_id = self.campaign.id
        old_skey = f"campaign:{camp_id}:account:{old_mac}:records:{status}"
        new_skey = f"campaign:{camp_id}:account:{new_mac}:records:{status}"
        # if no records specified, move all
        if len(records) < 1:
            records = self.my_redis.smembers(old_skey)

        # for record_id in records:
        #     self.my_redis.sadd(new_skey, record_id)
        #     self.my_redis.srem(old_skey, record_id)

        #     # get old status, move from old status to new status
        #     # old_status = self.my_redis.hset(record_id, "record_status")
        #     old_status = self.my_redis.hget(record_id, "record_status")
        #     old_lkey = f"campaign:{camp_id}:records:{old_status}"
        #     new_lkey = f"campaign:{camp_id}:records:{status}"

        #     self.my_redis.lrem(old_lkey, 0, record_id)
        #     self.my_redis.lrem(new_lkey, 0, record_id)
        #     self.my_redis.rpush(new_lkey, record_id)

        #     # update record data
        #     if new_mac == 'none':
        #         self.my_redis.hset(record_id, "mail_account_id", "")
        #     else:
        #         self.my_redis.hset(record_id, "mail_account_id", new_mac)

        if len(records):
            with self.my_redis.pipeline() as pipe:

                for record_id in records:
                    pipe.sadd(new_skey, record_id)
                    pipe.srem(old_skey, record_id)

                    # get old status, move from old status to new status
                    # old_status = pipe.hset(record_id, "record_status")
                    old_status = pipe.hget(record_id, "record_status")
                    old_lkey = f"campaign:{camp_id}:records:{old_status}"
                    new_lkey = f"campaign:{camp_id}:records:{status}"

                    # pipe.lrem(old_lkey, 0, record_id)
                    pipe.srem(old_lkey, record_id)
                    # pipe.lrem(new_lkey, 0, record_id)
                    # pipe.rpush(new_lkey, record_id)
                    pipe.sadd(new_lkey, record_id)

                    # update record data
                    if new_mac == 'none':
                        pipe.hset(record_id, "mail_account_id", "")
                    else:
                        pipe.hset(record_id, "mail_account_id", new_mac)

                pipe.execute()

        return True

    # debug only
    def changeAccountRecordsStatus(self, old_status=RS_PROCESSING, new_status=RS_SUCCESS, records=[]):
        camp_id = self.campaign.id
        mac_id = self.account.id

        old_skey = f"campaign:{camp_id}:account:{mac_id}:records:{old_status}"
        new_skey = f"campaign:{camp_id}:account:{mac_id}:records:{new_status}"

        old_lkey = f"campaign:{camp_id}:records:{old_status}"
        new_lkey = f"campaign:{camp_id}:records:{new_status}"

        # rootLogger.info(old_skey + "==>" + new_skey)
        # rootLogger.info(old_lkey + "==>" + new_lkey)

        # if no records specified, move all
        if len(records) < 1:
            records = self.my_redis.smembers(old_skey)

        # for item in records:
        #     self.my_redis.smove( old_skey, new_skey, item)
        #     self.my_redis.lrem( old_lkey, 0, item)
        #     self.my_redis.lrem( new_lkey, 0, item)
        #     self.my_redis.rpush( new_lkey, item)
        #     self.my_redis.hset( item, "record_status", new_status)

        if len(records):
            with self.my_redis.pipeline() as pipe:

                for item in records:
                    # pipe.smove( old_skey, new_skey, item)
                    # pipe.lrem( old_lkey, 0, item)
                    # pipe.lrem( new_lkey, 0, item)
                    # pipe.rpush( new_lkey, item)
                    pipe.hset( item, "record_status", new_status)

                # optimize actions
                pipe.srem(old_skey, *records)
                pipe.sadd(new_skey, *records)

                # optimize actions
                pipe.srem(old_lkey, *records)
                pipe.sadd(new_lkey, *records)

                pipe.execute()


        return True

    # i guess this one is deprecated...
    # def getMailDump(self, from_mail):
    #     camp_id = self.campaign.id
    #     mac_id = self.account.id
    #     hkey = f"campaign:{camp_id}:account:{mac_id}:maildumps"
    #     return self.my_redis.hget(hkey, from_mail)

    def getDlLinks(self, links_url='https://5.2.67.175:8443/transfers'):
        try:
            # res = requests.get(links_url, verify=False, timeout=600, proxies=dict(http=f'socks5://{self.sock_data}',
            #                      https=f'socks5://{self.sock_data}'))
            res = requests.get(links_url, verify=False, timeout=600)
            if res and res.ok and res.status_code > 199 and res.status_code < 400:
                # got string where properties are singlequoted, json demands doublequoted, so make small hack
                self.dl_links = json.loads( res.text.replace("'", '"') )

                # exclude possible empty urls
                self.dl_links = [item for  item in self.dl_links if len(item['url']) > 0]

                # process all links time
                str_format = '%Y%m%d%H%M%S'
                for item in self.dl_links:
                    item['time'] = datetime.datetime.strptime(item['time'], str_format)

                # leave only 24hrs links
                # min_date = datetime.datetime.utcnow() - datetime.timedelta(hours=10)
                min_date = datetime.datetime.utcnow() - datetime.timedelta(hours=300)
                self.dl_links = [item for item in self.dl_links if item['time'] > min_date]

                # now sort by time
                self.dl_links.sort(reverse=True, key=lambda x: x['time'])

                # and leave latest 500
                self.dl_links = self.dl_links[0:500]

                rootLogger.info(f"{self.prefix} getDlLinks got {len(self.dl_links)}, min_date:{self.dl_links[0]['time']}, max_time:{self.dl_links[-1]['time']}")
            else:
                rootLogger.warning(f"{self.prefix} getDlLinks got not good res:{res}, {res.status_code}, {res.text}")

        except Exception as e:
            rootLogger.error(f"{self.prefix} getDlLinks:{e}")

        if len(self.test_dl_links):
            rootLogger.info(f"{self.prefix} getDlLinks: got test_dl_links, override behaviour")
            self.dl_links = list(self.test_dl_links)

    def updateSettings(self, _new_settings):
        # make copy of settings
        self.settings = dict(_new_settings)

    def updateSocks(self, _new_socks):
        return True
        # current_socks_ids = [item['id'] for item in self.socks]
        # # append items
        # append_new = [item for item in _new_socks if item['id'] not in current_socks_ids]

        # # remove items
        # new_socks_ids = [item['id'] for item in _new_socks]
        # removal_ids = [item['id'] for item in self.socks if item['id'] not in new_socks_ids]

        # self.threadLock.acquire(blocking=True, timeout=300)
        # try:

        #     # remove bad items
        #     for item in self.socks:
        #         if item['id'] in removal_ids:
        #             self.socks.remove( item )

        #     # append new items
        #     self.socks.extend( append_socks )

        # except Exception as e:
        #     rootLogger.error(f"{self.prefix}[updateSocks]:{e}")
        # finally:
        #     if self.threadLock.locked():
        #         self.threadLock.release()
