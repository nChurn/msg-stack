from html.parser import HTMLParser
from html.entities import name2codepoint
import xml.etree.ElementTree as ET
import json

import concurrent.futures
import urllib.request

import socket, requests, time, datetime, threading

from includes.RootLogger import rootLogger
import includes.Database as db

import os
from os.path import join, dirname
from dotenv import load_dotenv
import redis

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
env_max_connections = int(os.getenv('REDIS_MAX_CONN', default=1024))

# Use a thread-safe blocking connection pool.
redis_conn_pool = redis.BlockingConnectionPool(
    host=env_host,
    port=env_port,
    max_connections=env_max_connections,
    decode_responses=env_decode_responses,
    timeout=300,
)


class MyHTMLParser(HTMLParser):
    urls = []
    prefix = "https://autoconfig.thunderbird.net/v1.1/"

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr[0] == 'href' and attr[1] != '/' and not attr[1].startswith('?'):
                self.urls.append(self.prefix + attr[1])

# Retrieve a single page and report the URL and contents
def load_url(url, timeout=300):
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        return conn.read()

def processXMLResult(data, my_redis):
    tree = ET.fromstring(data.decode('utf-8'))

    for child in tree[0].iter('domain'):
        key = f"{child.text}"

        domain_data = {}
        for iterator in (tree[0].iter('incomingServer'), tree[0].iter('outgoingServer')):
            # smtp, pop3 and imap
            for proto in iterator:
                proto_key = proto.attrib['type']
                if not proto_key in domain_data:
                    domain_data[proto_key] = []

                host = proto.find('hostname').text
                port = proto.find('port').text
                socketType = proto.find('socketType').text
                auth = proto.find('authentication').text
                domain_data[proto_key].append( {"host":host, "port":int(port), "socketType": socketType, "auth": auth} )

        # my_redis.set(f"isp:domain:{key}", json.dumps(domain_data))
        # with threadLock:
        db.setDomainData(key, domain_data, my_redis)

threadLock = threading.Lock()

my_redis = None

# run main function
if __name__ == '__main__':
    start_time = time.time()
    rootLogger.info(f"Begin")

    # create redis instance to share among all futher processes
    my_redis = redis.Redis(connection_pool=redis_conn_pool, decode_responses=env_decode_responses)


    rootLogger.info(f"Download index page...")
    try:
        raw_html = load_url('https://autoconfig.thunderbird.net/v1.1/', 120).decode('utf-8')
        rootLogger.info(f"...done")
        rootLogger.info(f"Parsing index page...")
        parser = MyHTMLParser()
        parser.feed(raw_html)
        rootLogger.info(f"...done")

        rootLogger.info(f"Start paralel processing for all domains...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            # Start the load operations and mark each future with its URL
            future_to_url = {executor.submit(load_url, url, 300): url for url in parser.urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    # print('%r generated an exception: %s' % (url, exc))
                    rootLogger.error(f"{url} result:{exc}")
                else:
                    processXMLResult(data, my_redis)

        rootLogger.info(f"...done")

        check_host = parser.urls[0].replace(parser.prefix, '')

        ispdb = db.getDomainData(check_host, my_redis)
        rootLogger.info(f"Check {check_host} data:{ispdb}")
        variants = [(item['host'], item['port'], True if item['socketType'] == 'SSL' else False, True if item['socketType'] == 'STARTTLS' else False) for item in ispdb['smtp']]
        rootLogger.info(f"Variants {variants}")

        # calculate time
        end_time = time.time()
        time_delta = end_time - start_time
        rootLogger.info(f"All processes are finnished, processing done tasks in {datetime.timedelta(seconds=time_delta)}")

        # sleep for 5 days
        sleep_time = 5*60*60*24
        time.sleep(sleep_time)
    except Exception as e:
        rootLogger.error(f"{e}")

        # sleep for 15 min
        sleep_time = 60*15
        time.sleep(sleep_time)
