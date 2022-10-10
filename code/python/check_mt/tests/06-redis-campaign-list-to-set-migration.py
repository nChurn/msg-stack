import sys
# sys.path.append("/code/python/check_mt")
import pathlib
sys.path.append(f"{pathlib.Path(__file__).parent.parent.absolute()}")


import tracemalloc
import socket, requests, time, datetime, threading
import concurrent.futures
from includes.RootLogger import rootLogger
from includes.RedisWrapperClass import RedisWrapperClass
import includes.Database as db
#
# from includes.CampaignThread import CS_CREATED, CS_PROCESSING, CS_PAUSED, CS_HIBERNATED, CS_COMPLETED, CS_DELETED
# from webmails.WebMailClass import display
# if display.is_started:
#	 display.stop()

import traceback
import random
import ssl
import re

import sys
import string
import os

from dotenv import load_dotenv
from os.path import join, dirname
import redis
import json

import string
import mmh3

def randomString(self, size_min, size_max=0, chars=string.ascii_letters + string.digits):
	if size_max == 0:
		gen_size = size_min
	else:
		gen_size = random.randint(size_min, size_max)

	return ''.join(random.choice(chars) for _ in range(gen_size))



if __name__ == "__main__":

	cmp_id = int(sys.argv[1])
	# max_items = int(sys.argv[2])
	my_redis = RedisWrapperClass()

	time_start_global = time.time()

	for status  in range(6):
		list_key_from = f"campaign:{cmp_id}:records:{status}"

		# get  all records
		if not bool(int( my_redis.exists(list_key_from) )):
			print(f"key:{list_key_from} not exists, skip")
			continue

		# if type of key allready set - skip
		if my_redis.type(list_key_from) == "set":
			print(f"key:{list_key_from} allready set, skip")
			continue

		# get  all records
		time_start = time.time()
		records = my_redis.lrange(list_key_from , 0, -1 )
		time_end = time.time()
		time_delta = time_end - time_start
		print(f"lrange {list_key_from} {len(records)} records in {datetime.timedelta(seconds=time_delta)}")
		# print("-"*125 + "\n")

		# remove item
		my_redis.delete(list_key_from)

		# append items to set instead of list
		time_start = time.time()
		my_redis.sadd(list_key_from, *records)
		time_end = time.time()
		time_delta = time_end - time_start
		print(f"sadd {list_key_from} {len(records)} records in {datetime.timedelta(seconds=time_delta)}")
		print("-"*125 + "\n")


	time_end = time.time()
	time_delta = time_end - time_start_global
	print(f"All done in {datetime.timedelta(seconds=time_delta)}")
	print("-"*125 + "\n")
