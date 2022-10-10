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

	bc_socks = db.getBCSocks()

	# bc_socks:[('81.17.23.125:22939',), ('151.80.241.109:25393',), ('185.45.193.25:2494',), ('185.45.193.25:19804',), ('185.45.193.25:4156',), ('151.80.241.109:43011',), ('81.17.23.125:35228',), ('151.80.241.109:5183',), ('185.45.193.25:3299',), ('185.45.193.25:35566',), ('185.45.193.25:4111',), ('185.45.193.25:20861',), ('151.80.241.109:16933',), ('151.80.241.109:15681',), ('81.17.23.125:41908',)]
	print(f"bc_socks:{bc_socks}")

	# first item:81.17.23.125:22939
	print(f"first item:{bc_socks[0].addr}")
