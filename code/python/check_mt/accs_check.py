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
            rootLogger.info(f"provideSock: sock[{sock['id']}] with {sock['processes']} processes")
            sock['processes'] += 1
            proxy = sock
            break

    # for sock in socks:
    #     if sock['processes'] < int(settings['process_per_proxy']) and sock['id'] not in blacklist:
    #         # easy hack for web accounts: their socks are same
    #         if web_acc and int(sock['port']) != 1550:
    #             continue
    #         sock['processes'] += 1
    #         proxy = sock

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


    # first of all check if we arlier try this account
    if account.checked_at != None and account.smtp_alive == 1:
        # check if account is chected before
        rootLogger.info(f"Account[{account.id}] SMTP normal account check")
        variants = [(account.smtp_host, account.smtp_port, account.smtp_ssl, account.smtp_starttls)]

    elif account.checked_at is None:

        # get first non-empty variant
        mail_user = next((item for item in logins if len(item) > 0), None)
        mail_password = next((item for item in passwords if len(item) > 0), None)

        # check if first timer but has all necesseary data
        # with help of redis hosts try to get proper settings for current record
        spl = re.split('[\@\#\%]', mail_user)
        check_host = spl[-1]

        ispdb = db.getDomainData(check_host, my_redis)
        if ispdb and 'smtp' in ispdb:
            rootLogger.info(f"Account[{account.id}] SMTP ispdb check active")
            variants = [(item['host'], item['port'], True if item['socketType'] == 'SSL' else False, True if item['socketType'] == 'STARTTLS' else False) for item in ispdb['smtp']]

    # if no variants found in ipsdb or account was
    if len(variants) < 1:
        rootLogger.info(f"Account[{account.id}] SMTP bruteforce check")

        # get first non-empty variant
        mail_user = next((item for item in logins if len(item) > 0), None)
        mail_password = next((item for item in passwords if len(item) > 0), None)
        tmp_host = next((item for item in hosts if len(item) > 0), None)

        if None in (mail_user, mail_password, tmp_host):
            error = f"Not enough data for check account: host, login or password."
            return res, error

        # extend host with all possible variants
        tmp_hosts = [tmp_host]
        # rootLogger.info(f"Account[{account.id}] tmp_hosts:{tmp_hosts}")
        replace_words = ["imap.", "pop.", "pop3.", "imap4."]
        for word in replace_words:
            # also check if this prefixes never checked before
            if word in tmp_host:
                ext = [ tmp_host.replace(word, prefix) for prefix in ["smtp.", "smtps.", "smtp2.", "mail.", "mail2.", "email.", "smtpout.", "mx1.", "smtpauth.", "authsmtp.", "webmail.", "smtp3."] ]
                tmp_hosts.extend(ext)
                # remove original replaceble
                tmp_hosts.pop(0)

        # if not, do two checks: if port is zero, try all ports
        if account.smtp_port == 0:
            ports = (
                # put default protocol cases firstly
                (25,    False,  False),
                (465,   True,   False),
                (587,   False,  True),
                (2525,  False,  False),

                # 25 - default is plain text
                (25,    True,   False),
                (25,    False,  True ),
                # 465 - default is ssl
                (465,   False,  False),
                (465,   False,  True),
                # 587 - default is starttls
                (587,   False,  False),
                (587,   True,   False),
                # 2525 - default is plain text
                (2525,  True,   False),
                (2525,  False,  True ),
            )
        else:
            if account.smtp_starttls > 0:
                ports = (
                    (account.smtp_port, False, True),
                    (account.smtp_port, True, True)
                )
            else:
                ports = (
                    (account.smtp_port, False, False),
                    (account.smtp_port, True, False),
                    (account.smtp_port, False, True)
                )

        variants = []
        for mail_host in tmp_hosts:
            for port in ports:
                variants.append((mail_host, port[0], port[1], port[2]))


    # this variant generates over 9000 parallel tasks, attempting to execute 'em...
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

    # iterate through all host/portt/ssl combos
    # outer_break = False
    # for mail_host in tmp_hosts:
    #     for port in ports:
    #         # rootLogger.info(f"Account[{account.id}] SMTP try combo:{mail_host}/{port[0]}/{port[1]}/{port[2]} host/port/ssl/starttls")
    #         alive, error = check_smtp(sock_data, account=account, mail_host=mail_host, mail_port=port[0], mail_user=mail_user, mail_password=mail_password, mail_ssl=port[1], mail_starttls=port[2])

    #         res.update({
    #             'smtp_host': mail_host,
    #             'smtp_port': port[0],
    #             'smtp_login': mail_user,
    #             'smtp_password': mail_password,
    #             'smtp_ssl': int(port[1]),
    #             'smtp_alive': alive,
    #             'smtp_starttls': int(port[2])
    #         })

    #         # if auth error - stop any other processings
    #         if error is not None:
    #             for err_tpl in auth_error_list:
    #                 if err_tpl in error.lower():
    #                     rootLogger.info(f"Account[{account.id}] found auth error, stop futher checks.")
    #                     outer_break = True

    #         # stop any futher checkings if alive
    #         if alive > 0 or outer_break:
    #             outer_break = True
    #             break

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

    # first of all check if we arlier try this account
    if account.checked_at != None and account.imap_alive == 1:
        rootLogger.info(f"Account[{account.id}] POP3 normal account check, {account.id}")
        variants = [(account.imap_host, account.imap_port, account.imap_ssl)]
        alive, error = check_pop3(sock_data, account)
        res['pop3_alive'] = alive
    elif account.checked_at is None:
        rootLogger.info(f"Account[{account.id}] POP3 ispdb check active")

        # get first non-empty variant
        mail_user = next((item for item in logins if len(item) > 0), None)
        mail_password = next((item for item in passwords if len(item) > 0), None)

        # check if first timer but has all necesseary data
        # with help of redis hosts try to get proper settings for current record
        spl = re.split('[\@\#\%]', mail_user)
        check_host = spl[-1]

        ispdb = db.getDomainData(check_host, my_redis)
        if ispdb and 'pop3' in ispdb:
            variants = [(item['host'], item['port'], True if item['socketType'] == 'SSL' else False) for item in ispdb['pop3']]
        # alive, error = check_imap(sock_data, account)
        # res['pop3_alive'] = alive


    if len(variants) < 1:
        # get first non-empty variant
        hosts = [account.pop3_host, account.smtp_host, account.imap_host]
        logins = [account.pop3_login, account.smtp_login, account.imap_login]
        passwords = [account.pop3_password, account.smtp_password, account.imap_password]

        # rootLogger.info(f"Account[{account.id}] passwords: {passwords}")

        mail_user = next((item for item in logins if len(item) > 0), None)
        mail_password = next((item for item in passwords if len(item) > 0), None)
        tmp_host = next((item for item in hosts if len(item) > 0), None)

        if None in (mail_user, mail_password, tmp_host):
            error = f"Not enough data for check account: host, login or password."
            return res, error

        # extend host with all possible variants
        tmp_hosts = [tmp_host]
        # rootLogger.info(f"Account[{account.id}] tmp_hosts:{tmp_hosts}")
        replace_words = ["smtp.", "imap.", "imap4.", "smtps.", "smtp2.", "mail.", "mail2.", "email.", "smtpout.", "mx1.", "smtpauth.", "authsmtp.", "webmail.", "smtp3."]
        for word in replace_words:
            # also check if this prefixes never checked before
            if word in tmp_host:
                ext = [ tmp_host.replace(word, prefix) for prefix in ["pop.", "pop3.", "mail."] ]
                tmp_hosts.extend(ext)
                tmp_hosts.pop(0)

        # if port is zero, try all ports
        if account.pop3_port == 0:
            ports = (
                # default for 110 port
                (110, False),
                (110, True),
                # default for 995 port
                (995, True),
                (995, False)
            )
        else:
            ports = ((account.pop3_port, False), (account.pop3_port, True))

        variants = []
        for mail_host in tmp_hosts:
            for port in ports:
                variants.append((mail_host, port[0], port[1]))

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
                    # if auth error - stop any other processings
                    for err_tpl in auth_error_list:
                        if err_tpl in variant_error.lower():
                            rootLogger.info(f"Account[{account.id}] POP3 found auth error, mark it as error")
                            # assign error
                            error = f"{variant_error}"
                            break

                    for err_tpl in wrong_ssl_list:
                        if err_tpl.lower() in variant_error.lower():
                            rootLogger.info(f"Account[{account.id}] POP3 found ssl error, mark it as error")
                            # assign error
                            error = f"{variant_error}"
                            break

        # # iterate through all host/portt/ssl combos
        # outer_break = False
        # for mail_host in tmp_hosts:
        #     if outer_break:
        #         break

        #     for port in ports:
        #         # rootLogger.info(f"Account[{account.id}] POP3 try combo:{mail_host}/{port[0]}/{port[1]} host/port/ssl")
        #         alive, error = check_pop3(sock_data, account=account, mail_host=mail_host, mail_port=port[0], mail_user=mail_user, mail_password=mail_password, mail_ssl=port[1])

        #         res.update({
        #             'pop3_host': mail_host,
        #             'pop3_port': port[0],
        #             'pop3_login': mail_user,
        #             'pop3_password': mail_password,
        #             'pop3_ssl': int(port[1]),
        #             'pop3_alive': alive
        #         })

        #         # if auth error - stop any other processings
        #         if error is not None:
        #             for err_tpl in auth_error_list:
        #                 if err_tpl in error.lower():
        #                     rootLogger.info(f"Account[{account.id}] POP3 found auth error, stop futher checks.")
        #                     outer_break = True
        #                     break

        #         # stop any futher checkings if alive
        #         if alive > 0 or outer_break:
        #             outer_break = True
        #             break

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

    # first of all check if we arlier try this account
    if account.checked_at != None and account.imap_alive == 1:
        rootLogger.info(f"Account[{account.id}] IMAP normal account check, {account.id}")
        variants = [(account.imap_host, account.imap_port, account.imap_ssl)]

    elif account.checked_at is None:
        rootLogger.info(f"Account[{account.id}] IMAP ispdb check active")

        # get first non-empty variant
        mail_user = next((item for item in logins if len(item) > 0), None)
        mail_password = next((item for item in passwords if len(item) > 0), None)

        # check if first timer but has all necesseary data
        # with help of redis hosts try to get proper settings for current record
        spl = re.split('[\@\#\%]', mail_user)
        check_host = spl[-1]

        ispdb = db.getDomainData(check_host, my_redis)
        if ispdb and 'imap' in ispdb:
            variants = [(item['host'], item['port'], True if item['socketType'] == 'SSL' else False) for item in ispdb['imap']]
        # alive, error = check_imap(sock_data, account)
        # res['imap_alive'] = alive


    if len(variants) < 1:
        # get first non-empty variant
        hosts = [account.imap_host, account.smtp_host, account.pop3_host]
        logins = [account.imap_login, account.smtp_login, account.pop3_login]
        passwords = [account.imap_password, account.smtp_password, account.pop3_password]

        # rootLogger.info(f"Account[{account.id}] passwords: {passwords}")

        mail_user = next((item for item in logins if len(item) > 0), None)
        mail_password = next((item for item in passwords if len(item) > 0), None)
        tmp_host = next((item for item in hosts if len(item) > 0), None)

        if None in (mail_user, mail_password, tmp_host):
            error = f"Not enough data for check account: host, login or password."
            return res, error

        # extend host with all possible variants
        tmp_hosts = [tmp_host]
        # rootLogger.info(f"Account[{account.id}] tmp_hosts:{tmp_hosts}")
        replace_words = ["smtp.", "pop.", "pop3.", "smtps.", "smtp2.", "mail.", "mail2.", "email.", "smtpout.", "mx1.", "smtpauth.", "authsmtp.", "webmail.", "smtp3."]
        for word in replace_words:
            # also check if this prefixes never checked before
            if word in tmp_host:
                ext = [ tmp_host.replace(word, prefix) for prefix in ["imap.", "imap4.", "mail."] ]
                tmp_hosts.extend(ext)
                tmp_hosts.pop(0)

        # if not, do two checks: if port is zero, try all ports
        if account.imap_port == 0:
            ports = (
                # default for 143 port
                (143, False),
                (143, True),
                # default for 993 port
                (993, True),
                (993, False)
            )
        else:
            ports = ((account.imap_port, False), (account.imap_port, True))

        variants = []
        for mail_host in tmp_hosts:
            for port in ports:
                variants.append((mail_host, port[0], port[1]))


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

        # # iterate through all host/portt/ssl combos
        # outer_break = False
        # for mail_host in tmp_hosts:
        #     if outer_break:
        #         break

        #     for port in ports:
        #         # rootLogger.info(f"Account[{account.id}] IMAP try combo:{mail_host}/{port[0]}/{port[1]} host/port/ssl")
        #         alive, error = check_imap(sock_data, account=account, mail_host=mail_host, mail_port=port[0], mail_user=mail_user, mail_password=mail_password, mail_ssl=port[1])

        #         res.update({
        #             'imap_host': mail_host,
        #             'imap_port': port[0],
        #             'imap_login': mail_user,
        #             'imap_password': mail_password,
        #             'imap_ssl': int(port[1]),
        #             'imap_alive': alive
        #         })

        #         # if auth error - stop any other processings
        #         if error is not None:
        #             for err_tpl in auth_error_list:
        #                 if err_tpl in error.lower():
        #                     rootLogger.info(f"Account[{account.id}] IMAP found auth error, stop futher checks.")
        #                     outer_break = True
        #                     break

        #         # stop any futher checkings if alive
        #         if alive > 0 or outer_break:
        #             outer_break = True
        #             break

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
        rootLogger.info(f"Account[{self.prefix}] Begin check")
        # time.sleep(random.randrange(5, 15))

        # check if we got web-acc
        if self.account.web_url and self.account.web_login and self.account.web_password:
            rootLogger.info(f"Account[{self.prefix}] Web account check")
            try:
                # from includes.webmails.WebMailClass import WebMailClass
                # creates session with sock data and
                # WebMailClass(self.sock_data['host'], web_acc_proxy_port).StartSession(login, password, url ,True).close()
                prefix=f"Account[{self.prefix}]WEB: "
                with WEBMailProcessor( account=self.account, socks_creds=self.sock_data, ssl_context=None, prefix=prefix) as server:
                    folder_list = server.getFolders()

                self.result.update({
                    'web_alive': 1,
                    'alive': 1
                })
            except Exception as e:
                self.result.update({
                    'has_errors': 1,
                    'error_log':{'WEB': f'{e}'},
                    'error_at': datetime.datetime.utcnow()
                })
                # rootLogger.error(f"Account[{self.prefix}] web check:{e}")
                raise e

            # done a bit earlier
            return True

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

def addThread(threads, account, proxy, max_threads):
    if proxy:
        new_thread = AccCheckThread(account, proxy, prefix=f"{account.id}", max_threads=max_threads)
        new_thread.daemon = True
        new_thread.start()
        threads.append( new_thread )
    else:
        rootLogger.info("No free proxy to add worker")

    return threads

# run main function
if __name__ == '__main__':
    start_time = time.time()
    rootLogger.info(f"Begin")

    # socks check interval
    sci = 300
    last_check = int(time.time())

    # get all socks for checking
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
    settings = {}

    try:
        settings = db.getSystemSettings()['acc_checker']
        rootLogger.info(f"System settings: {settings}")
    except Exception as e:
        rootLogger.error(f"db.getSystemSettings:{e}")
        rootLogger.info(f"Sleep for 5 minutes and try again")
        time.sleep(5*60)
        sys.exit(0)
        # raise e

    # calculate chunk size
    chunk_size = min(int(settings['number_process']), len(socks)*int(settings['process_per_proxy']))
    rootLogger.info(f"Calculated chunk size: {chunk_size} from {int(settings['number_process'])} and {len(socks)*int(settings['process_per_proxy'])}")

    if 'min_hours' not in settings:
        settings['min_hours'] = 3

    # get all accounts for checking
    accounts = db.getCheckAccounts(hours_delta=int(settings['min_hours']))
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

                rootLogger.info(f"Thread[{thread.prefix}] done, get result: {result}")
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

                                threads = addThread(threads, thread.account, proxy, int(settings['threads_per_protocol']))
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
                    account = accounts.next()
                    rootLogger.info(f"Get next account: {account.id}")
                    proxy = provideSock(socks, ['abc'], settings)
                    if proxy is None:
                        rootLogger.info(f"No proxy to provide: {account.id}")
                        break
                    # else:
                    #     rootLogger.info(f"Provided proxy{proxy['host']}:{proxy['port']} from {socks}")

                    threads = addThread(threads, account, proxy, int(settings['threads_per_protocol']))
                    rootLogger.info(f"Threads amount:{len(threads)}")
                except Exception as e:
                    rootLogger.info(f"But no more account to check:{e}")
                    account = None
                    break

        # update database with account check result
        if len(results):
            db.setCheckAccounts(results)

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
