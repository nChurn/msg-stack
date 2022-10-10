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
	max_items = int(sys.argv[2])
	my_redis = RedisWrapperClass()

	max_list_len = 500000

	# for i in range(1000000):

	# 	# cmp_id = 216
	# 	from_mail = randomString(5, 10)
	# 	from_name = randomString(5, 10)
	# 	address = randomString(5, 10) + "@" + randomString(5, 10) + ".com"

	# 	hash_id = hex(mmh3.hash64(f"{cmp_id}{from_mail}{from_name}{address}")[0] & 0xffffffffffffffff)[2:]
	# 	hash_key = f"campaign:{cmp_id}:record:{hash_id}"

	# 	my_redis.lpush(f"campaign:{cmp_id}:records:0", hash_id)
	# 	my_redis.sadd(f"campaign:{cmp_id}:account:101:records:0", hash_id)


	list_key_from = f"campaign:{cmp_id}:records:0"
	list_key_to = f"campaign:{cmp_id}:records:2"

	set_key_from = f"campaign:{cmp_id}:account:101:records:0"
	set_key_to = f"campaign:{cmp_id}:account:101:records:2"

	sort_set_key_from = f"campaign:{cmp_id}:account:101:sort:records:0"
	sort_set_key_to = f"campaign:{cmp_id}:account:101:sort:records:2"

	# clear all data
	for key in ( list_key_from, list_key_to, set_key_from, set_key_to, sort_set_key_from, sort_set_key_to ):
		my_redis.delete(key)

	# ====================================================================================================
	items = []
	time_start = time.time()
	for i in range(max_items):
		from_mail = randomString(5, 10)
		from_name = randomString(5, 10)
		address = randomString(5, 10) + "@" + randomString(5, 10) + ".com"

		hash_id = hex(mmh3.hash64(f"{cmp_id}{from_mail}{from_name}{address}")[0] & 0xffffffffffffffff)[2:]
		hash_key = f"campaign:{cmp_id}:record:{hash_id}"

		items.append(hash_key)
	time_end = time.time()
	time_delta = time_end - time_start
	print(f"generated {len(items)} items in {datetime.timedelta(seconds=time_delta)}")
	print("-"*125 + "\n")


	# # ====================================================================================================
	# if len(items) < max_list_len:
	# 	time_start = time.time()
	# 	my_redis.lpush(list_key_from, *items)
	# 	time_end = time.time()
	# 	time_delta = time_end - time_start
	# 	print(f"lpush {list_key_from} ({len(items)}) in {datetime.timedelta(seconds=time_delta)}")
	# 	print("-"*125 + "\n")
	# 	# time.sleep(5)
	# else:
	# 	print(f"lpush {list_key_from} ({len(items)}) skipped - too much items!")


	# # ====================================================================================================
	# time_start = time.time()
	# my_redis.sadd(set_key_from, *items)
	# time_end = time.time()
	# time_delta = time_end - time_start
	# print(f"sadd {set_key_from} ({len(items)}) in {datetime.timedelta(seconds=time_delta)}")
	# print("-"*125 + "\n")

	# # free some memory
	# # del items[:]
	# # time.sleep(5)

	# # ====================================================================================================
	# if len(items) < max_list_len:
	# 	time_start = time.time()
	# 	records = my_redis.lrange(list_key_from , 0, -1 )
	# 	time_end = time.time()
	# 	time_delta = time_end - time_start
	# 	print(f"total_records lrange:{len(records)} in {datetime.timedelta(seconds=time_delta)}")
	# 	# time.sleep(5)

	# 	time_start = time.time()
	# 	with my_redis.pipeline() as pipe:
	# 		for record in records:
	# 			pipe.lrem(list_key_from, 0, record)
	# 			pipe.lpush(list_key_to, record)

	# 		pipe.execute()

	# 	time_end = time.time()
	# 	time_delta = time_end - time_start
	# 	print(f"lrem->lpush:{len(records)} in {datetime.timedelta(seconds=time_delta)}")
	# 	print("-"*125 + "\n")
	# 	# time.sleep(5)
	# else:
	# 	print(f"lrem->lpush {list_key_from}->{list_key_to} ({len(items)}) skipped - too much items!")

	# # ====================================================================================================
	# time_start = time.time()
	# records = my_redis.smembers( set_key_from )
	# time_end = time.time()
	# time_delta = time_end - time_start
	# # print(f"total_records smembers:{len(records)} in {datetime.timedelta(seconds=time_delta)}")
	# # time.sleep(5)

	# time_start = time.time()
	# with my_redis.pipeline() as pipe:
	# 	for record in records:
	# 		pipe.srem(set_key_from, record)
	# 		pipe.sadd(set_key_to, record)

	# 	pipe.execute()

	# time_end = time.time()
	# time_delta = time_end - time_start
	# print(f"srem->sadd:{len(records)} in {datetime.timedelta(seconds=time_delta)}")
	# print("-"*125 + "\n")
	# # time.sleep(5)


	# # ====================================================================================================
	# time_start = time.time()
	# records = my_redis.smembers( set_key_to )
	# time_end = time.time()
	# time_delta = time_end - time_start
	# # print(f"total_records smembers:{len(records)} in {datetime.timedelta(seconds=time_delta)}")
	# # time.sleep(5)

	# time_start = time.time()
	# with my_redis.pipeline() as pipe:
	# 	pipe.srem(set_key_to, *records)
	# 	pipe.sadd(set_key_from, *records)
	# 	pipe.execute()

	# time_end = time.time()
	# time_delta = time_end - time_start
	# print(f"srem->sadd(all):{len(records)} in {datetime.timedelta(seconds=time_delta)}")
	# print("-"*125 + "\n")
	# # time.sleep(5)


	# # ====================================================================================================
	# time_start = time.time()
	# records = my_redis.smembers( set_key_from )
	# time_end = time.time()
	# time_delta = time_end - time_start
	# # print(f"total_records smembers:{len(records)} in {datetime.timedelta(seconds=time_delta)}")
	# # time.sleep(5)

	# time_start = time.time()
	# with my_redis.pipeline() as pipe:
	# 	for record in records:
	# 		pipe.smove(set_key_to, set_key_from, record)

	# 	pipe.execute()

	# time_end = time.time()
	# time_delta = time_end - time_start
	# print(f"smove:{len(records)} in {datetime.timedelta(seconds=time_delta)}")
	# print("-"*125 + "\n")

	# ====================================================================================================
	time_start = time.time()
	with my_redis.pipeline() as pipe:
		for record in items:
			pipe.zadd(sort_set_key_to, {record: time.time()})

		pipe.execute()

	time_end = time.time()
	time_delta = time_end - time_start
	print(f"zadd:{len(items)} in {datetime.timedelta(seconds=time_delta)}")
	print("-"*125 + "\n")


	# ====================================================================================================
	time_start = time.time()
	records = my_redis.zrange( sort_set_key_to, 0, -1 )
	time_end = time.time()
	time_delta = time_end - time_start
	print(f"total_records zrange:{len(records)} in {datetime.timedelta(seconds=time_delta)}")
	print("-"*125 + "\n")


	# ====================================================================================================
	time_start = time.time()
	my_redis.zadd( sort_set_key_from, {record: time.time() for record in items} )
	time_end = time.time()
	time_delta = time_end - time_start
	print(f"zadd(alll):{len(items)} in {datetime.timedelta(seconds=time_delta)}")
	print("-"*125 + "\n")

