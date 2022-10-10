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
#     display.stop()

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


if __name__ == "__main__":

	cmp_id = int(sys.argv[1])

	my_redis = RedisWrapperClass()

	# get all accounts
	accounts = db.getCampaignAccounts(cmp_id)

	for account in accounts:
		rootLogger.info(f"Checking acocunt:{account.id}")
		total_records = my_redis.scard( f"campaign:{cmp_id}:account:{account.id}:records:2" )
		rootLogger.info(f"total_records:{total_records}")

    # if len(total_records) < 1:
    #     rootLogger.info(f"{self.prefix} account[{account.id}] has no records, skip")
    #     continue
