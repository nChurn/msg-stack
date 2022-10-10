import socket, requests, time, datetime, threading
import concurrent.futures

from includes.SMTPSocks import MYSMTP, MYSMTP_SSL
from includes.IMAP4Socks import MYIMAP4, MYIMAP4_SSL
from includes.POP3Socks import MYPOP3, MYPOP3_SSL
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

import random
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

def check_sock(sock_data, my_redis=None):
	rootLogger.info(f"Proxy[{sock_data['host']}:{sock_data['port']}] sleep for:{sock_data['sleep']}")
	time.sleep(int(sock_data['sleep']))

	rootLogger.info(f"Proxy[{sock_data['host']}:{sock_data['port']}] pseudo check is done")
	return sock_data


if __name__ == '__main__':
	chunk_size = 10

	# create redis instance to share among all futher processes
	my_redis = redis.Redis(connection_pool=redis_conn_pool, decode_responses=env_decode_responses)

	socks = []
	for i in range (170):
		socks.append( {
			'id': random.randint(5,125),
			'host': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
			'port': random.randint(1,65535),
			'alive': random.randint(0,1),
			'allow_smtp': random.randint(0,1),
			'sleep': random.randint(1,150)
		})


	with concurrent.futures.ThreadPoolExecutor(max_workers = chunk_size) as executor:
		my_futures = [executor.submit(check_sock, sock_data, my_redis) for widx, sock_data in enumerate(socks)]
		# save data ASAP
		rootLogger.info(f"my_futures amount:{len(my_futures)}")
		for future in concurrent.futures.as_completed(my_futures):
			sock_data = future.result()
			rootLogger.info(f"Proxy {sock_data['host']}:{sock_data['port']} check result: alive:{sock_data['alive']} allow_smtp[{sock_data['allow_smtp']}]")
			# db.updateSocks(socks=[sock_data])

		rootLogger.info(f"my_futures done.")

	rootLogger.info("Done")
