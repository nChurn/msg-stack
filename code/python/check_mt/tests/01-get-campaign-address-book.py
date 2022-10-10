import sys
# sys.path.append("/code/python/check_mt")
import pathlib
sys.path.append(f"{pathlib.Path(__file__).parent.parent.absolute()}")


import tracemalloc
import socket, requests, time, datetime, threading
import concurrent.futures
from includes.RootLogger import rootLogger
from includes.patch import patch
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

	all_campaigns = db.getCampaigns(status=None, _id=51)
	# print(f"all_campaigns:{all_campaigns}")

	try:
		first_one = next( all_campaigns )
	except Exception as e:
		first_one = all_campaigns

	print(f"First campaign:{first_one.id}")

	addresses = db.getCampaignAccountsAddresses( first_one.id )
	# print(f"First campaign addresses:{len(addresses)}")
