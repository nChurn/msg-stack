import socket, requests, time, datetime, threading
import concurrent.futures

from includes.SMTPSocks import MYSMTP, MYSMTP_SSL
from includes.IMAP4Socks import MYIMAP4, MYIMAP4_SSL
from includes.POP3Socks import MYPOP3, MYPOP3_SSL

import includes.Database as db
import includes.BanListIP as banlist_ip

from includes.RootLogger import rootLogger

# create banlist container, all functions etc will use it later
banlist = []
test_accs = []

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
env_max_connections = int(os.getenv('REDIS_MAX_CONN', default=128))

# Use a thread-safe blocking connection pool.
redis_conn_pool = redis.BlockingConnectionPool(
    host=env_host,
    port=env_port,
    max_connections=env_max_connections,
    decode_responses=env_decode_responses,
    timeout=300,
)


def checkIpInBanList(ip, banlist):
    occurencies1 = banlist_ip.checIpForDNSResolver( ip )
    occurencies2 = banlist_ip.checkIpInBlackList( ip, banlist )
    return occurencies1 + occurencies2

def check_smtp(sock_data, account):
    mail_host = account.smtp_host
    mail_port = account.smtp_port
    mail_user = account.smtp_login
    mail_password = account.smtp_password

    socks_creds = {
        'host': sock_data['host'],
        'port': int(sock_data['port']),
        'user': sock_data['login'],
        'password': sock_data['password']
    }

    result = 0
    try:
        if mail_port == 465:
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

        if mail_port == 587:
            server.starttls()

        server.ehlo_or_helo_if_needed()
        server.login(mail_user, mail_password)
        server.quit()
        rootLogger.info(f"Proxy {sock_data['host']}:{sock_data['port']} check {mail_user}:{mail_password}@{mail_host}:{mail_port} is ok")
        result = 1
    except Exception as e:
        rootLogger.info(f"Proxy {sock_data['host']}:{sock_data['port']} check {mail_user}:{mail_password}@{mail_host}:{mail_port} is not ok: {e}")
        # raise e
        result = 0

    return result

def check_sock(sock_data, my_redis=None):
    # get outer ip: as well as check for alive
    soc_str = f'socks5://{sock_data["login"]}:{sock_data["password"]}@{sock_data["host"]}:{sock_data["port"]}'
    proxies = {
        'http': soc_str,
        'https': soc_str
    }

    # resolve outer ip
    rootLogger.info(f"Check {sock_data['host']}:{sock_data['port']}")
    try:
        # r = requests.get('https://httpbin.org/ip', proxies=proxies)
        r = requests.get('http://curlmyip.net/', proxies=proxies, timeout=60)
        outer_ip = r.content.decode('utf8').rstrip()

        rootLogger.info(f"Outer ip for {sock_data['host']}:{sock_data['port']} is: {outer_ip}")
        sock_data['alive'] = 1
        sock_data['outer_ip'] = outer_ip
    except Exception as e:
        # rootLogger.error(f"Outer ip for {sock_data['host']}:{sock_data['port']} error: {e}")
        sock_data['alive'] = 0
        if my_redis:
            db.updateSocks(socks=[sock_data], _reids=my_redis)
        return sock_data

    # resolve dns
    data = [sock_data['outer_ip']]
    try:
        data = socket.gethostbyaddr(sock_data['outer_ip'])
    except Exception as e:
        pass

    sock_data['hostname'] = data[0]
    rootLogger.info(f"Hostname for {sock_data['host']}:{sock_data['port']} is: {data[0]}")

    # check for ip to occure in different banlist
    # if len(banlist) > 0 and sock_data["type"] != "grabber":
    sock_data['banlist'] = checkIpInBanList(sock_data['outer_ip'], banlist)

    # if found in banlist - no need for futher checks
    if len(sock_data['banlist']) > 0:
        rootLogger.error(f"{sock_data['host']}:{sock_data['port']} is marked in blacklists, stop check")
        if my_redis:
            db.updateSocks(socks=[sock_data], _reids=my_redis)
        return sock_data

    if len(test_accs) < 1:
        rootLogger.info(f"Proxy {sock_data['host']}:{sock_data['port']} no test accounts to check smtp")
        if my_redis:
            db.updateSocks(socks=[sock_data], _reids=my_redis)
        return sock_data

    smtp_max_workers = 3
    results = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers = smtp_max_workers) as executor:
        my_futures = [executor.submit(check_smtp, sock_data, account) for widx, account in enumerate(test_accs)]
        # save data ASAP
        for future in concurrent.futures.as_completed(my_futures):
            results += future.result()

    rootLogger.info(f"Proxy {sock_data['host']}:{sock_data['port']} smtp results:{results}/{len(test_accs)}")

    if results/len(test_accs) >= 2/3:
        rootLogger.info(f"Proxy {sock_data['host']}:{sock_data['port']} mark smtp as alive")
        sock_data['allow_smtp'] = 1
        sock_data['smtp_allow'] = 1
    else:
        rootLogger.info(f"Proxy {sock_data['host']}:{sock_data['port']} mark smtp as dead")
        sock_data['smtp_allow'] = 0
        sock_data['allow_smtp'] = 0

    if my_redis:
        db.updateSocks(socks=[sock_data], _reids=my_redis)

    return sock_data

# run main function
if __name__ == '__main__':
    start_time = time.time()
    rootLogger.info(f"Begin")

    sleep_time = 30
    socks_check_interval = 300

    # create redis instance to share among all futher processes
    my_redis = redis.Redis(connection_pool=redis_conn_pool, decode_responses=env_decode_responses)

    try:
        db.removeSocksJunkData(_reids=my_redis)
        db.removeFailedSocks(_reids=my_redis)
        # temporarly off
        # db_socks = db.getBCSocks()
        # rootLogger.info(f"[Main] db_socks:{db_socks}")
        # db.addSocks(socks=db_socks, _reids=my_redis)
    except Exception as e:
        rootLogger.error(f"Socks regain:{e}")
        # rootLogger.info(f"Sleep for 5 minutes and try again")
        # time.sleep(5*60)
        # return 0
        # sys.exit(0)


    # get all socks for checking
    socks = []
    try:
        socks = db.getSocks(socks_type='spam') + db.getSocks(socks_type='grabber') + db.getSocks(socks_type='checker')
    except Exception as e:
        # raise e
        rootLogger.error(f"db.getSocks:{e}")
        rootLogger.info(f"Sleep for 5 minutes and try again")
        time.sleep(5*60)
        # return 0
        sys.exit(0)



    # to avoid None VS Datetime comparision, assume None as long time not checked
    for item in socks:
        if item['checked_at'] is None:
            item['checked_at'] = datetime.datetime(2001, 1, 1, 0, 0, 1)

    dt_now = datetime.datetime.utcnow()

    # skip socks that are checked less tahn 5 minutes ago
    socks = [item for item in socks if (dt_now - item['checked_at']) > datetime.timedelta(seconds = socks_check_interval)]

    if len(socks) > 1:

        # create redis instance to share among all futher processes
        my_redis = redis.Redis(connection_pool=redis_conn_pool, decode_responses=env_decode_responses)

        rootLogger.info(f"Download banlist")
        banlist = banlist_ip.getBlackLists(False, True)

        test_accs = [acc for acc in db.getTestAccounts()]

        # get system settings
        max_processes = int(db.getSystemSettings()['socks_checker']['number_process'])
        rootLogger.info(f"System settings max_processes: {max_processes}")

        # calculate chunk size
        chunk_size = min(max_processes, len(socks))
        rootLogger.info(f"Calculated chunk size: {chunk_size}")

        with concurrent.futures.ThreadPoolExecutor(max_workers = chunk_size) as executor:
            my_futures = [executor.submit(check_sock, sock_data, my_redis) for widx, sock_data in enumerate(socks)]
            # save data ASAP
            for future in concurrent.futures.as_completed(my_futures):
                sock_data = future.result()
                rootLogger.info(f"Proxy {sock_data['host']}:{sock_data['port']} check result: alive:{sock_data['alive']} allow_smtp[{sock_data['allow_smtp']}]")
                # db.updateSocks(socks=[sock_data])
    else:
        rootLogger.info("No socks to check.")

    #
    end_time = time.time()
    time_delta = end_time - start_time
    rootLogger.info(f"All processes are finnished, processing done tasks in {datetime.timedelta(seconds=time_delta)}")
    time.sleep(sleep_time)
