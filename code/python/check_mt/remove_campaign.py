import includes.Database as db
import datetime
# import os
# import time
import sys


import traceback

import json
import email
import re

import os
from os.path import join, dirname
from dotenv import load_dotenv
# Create .env file path.
dotenv_path = join(dirname(__file__), 'includes/.env')
# Load file from the path.
load_dotenv(dotenv_path)
redis_host = os.getenv('REDIS_HOST')
# print("redis_host:{}".format(redis_host))

import time
from threading import Thread

RS_NEW = 0
RS_PROCESSING = 1
RS_SUCCESS = 2
RS_FAILED = 3
RS_SKIPPED = 4
RS_BLACKLIST = 5

cmp_id = int(sys.argv[1])

print(f"removeCampaign:{cmp_id}")

db.removeCampaign( cmp_id )
