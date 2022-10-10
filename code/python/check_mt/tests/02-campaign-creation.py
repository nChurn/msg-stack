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
from includes.CampaignThread import CS_CREATED, CS_PROCESSING, CS_PAUSED, CS_HIBERNATED, CS_COMPLETED, CS_DELETED
from webmails.WebMailClass import display
if display.is_started:
	rootLogger.info("Stopping X with display")
	display.stop()

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
import zlib

def my_crc32(my_str):
	return hex(zlib.crc32(my_str.encode('utf-8')) % (1<<32))

def rule_processor(record):
	r_name = f"r_{my_crc32(record.group + record.rule)}"
	ret = {
		'regex': f"(?P<{r_name}>{record.rule})",
		'rule': record.rule,
		'group': record.group,
		'r_name': r_name,
	}
	return ret

def processCampaignAccount(campaign, account, rule_regex=None, my_redis=None):
	from includes.SMTPThread import RS_NEW, RS_PROCESSING, RS_SUCCESS, RS_FAILED, RS_SKIPPED, RS_BLACKLIST

	if my_redis is None:
		my_redis = RedisWrapperClass()

	# raise Exception('pizdec')

	# get all contacts for account
	contacts = db.getAccountAddressBook( [account.id] )
	good_contacts = [item for item in contacts if not rule_regex.search( item.address )]
	fail_contacts = [item for item in contacts if rule_regex.search( item.address )]

	# save failed contacts immedeately
	fail_records = []
	for contact in fail_contacts:
		save_item = {
			'campaign_id': campaign.id,
			'mail_account_addressbook_id': contact.id,
			'mail_account_id': account.id,
			'spam_base_id': None,
			'spam_base_record_id': None,
			'address': contact.address,
			'name': contact.name,
			'company': contact.company,
			'rest': contact.rest,
			'record_status': RS_BLACKLIST,
			'record_status_txt': f'Blacklisted due to regex:{rule}',
			'dump_subject': '',
			'dump_body': '',
			'dump_headers': '',
		}
		fail_records.append( save_item )

	db.putRecordsToRedis( campaign=campaign, mail_account=account, records=fail_records, record_status=RS_BLACKLIST, record_status_txt='skipped via regexp', my_redis=my_redis )

	good_records = []
	# for normal contacts get whole
	for contact in good_contacts:
		conversation = db.getAddressBookContactConversation( account, contact, max_days=1000 )
		rootLogger.info(f"[processCampaignAccount({account.id})][{contact.id}]:{conversation}")

		dump_subject = next( (item.subject for item in conversation), '')
		dump_body = ''.join( [item.body for item in conversation] )
		dump_headers = json.dumps(next( (item.headers for item in conversation), {}))

		save_item = {
			'campaign_id': campaign.id, # $campaign_id,
			'mail_account_addressbook_id': contact.id, # property_exists($item , 'id') ? $item->id : null,
			'mail_account_id': account.id, # $mail_account_id,
			'spam_base_id': None, # property_exists($item , 'spam_base_id') ? $item->spam_base_id : null,
			'spam_base_record_id': None, # property_exists($item , 'spam_base_record_id') ? $item->spam_base_record_id : null,
			'address': contact.address, # $item->address,
			'name': contact.name, # $item->name,
			'company': contact.company, # $item->company,
			'rest': contact.rest, # $item->rest,
			'record_status': RS_NEW, # $record_status,
			'record_status_txt': '', # empty($item->record_status_txt) ? $record_status_txt : $item->record_status_txt,
			'dump_subject': dump_subject, # empty($item->dump_subject) ? '' : $item->dump_subject,
			'dump_body': dump_body, # empty($item->dump_body) ? '' : $item->dump_body,
			'dump_headers': dump_headers, # empty($item->dump_headers) ? '' : $item->dump_headers,
		}

		good_records.append( save_item )

	db.putRecordsToRedis( campaign=campaign, mail_account=account, records=fail_records, record_status=RS_NEW, record_status_txt='', my_redis=my_redis )


if __name__ == "__main__":

	all_campaigns = db.getCampaigns(status=None, name='universalio')
	# rootLogger.info(f"all_campaigns:{all_campaigns}")
	try:
		first_one = next( all_campaigns )
	except Exception as e:
		# first_one = all_campaigns
		rootLogger.info("no campaign, create new")
		my_campaign = db.createCampaign( status=CS_PAUSED, title='universalio', subject='Take a look at document attached' )

		all_campaigns = db.getCampaigns( status=None, name='universalio' )
		first_one = next( all_campaigns )


	rootLogger.info(f"First campaign:{first_one.id}")

	db.appendAccountsToCampaign(first_one.id)

	# # get all addresses - no reason as we might process per account in multithread
	# addresses = db.getCampaignAccountsAddresses( first_one.id )

	# generate filter for addresses
	rules = db.getCampaignScanRules( first_one.filters )
	rules_processed = [rule_processor(item) for item in rules]
	# rootLogger.info(f"rules_processed:{rules_processed}")

	if len( rules_processed ):
		rule_regex = "/" + "|".join( [item['regex'] for item in rules_processed] ) + "/i"
	else:
		rule_regex = "/^\!skip-me\!/"

	# rootLogger.info(f"rule_regex:{rule_regex}")
	rule_regex = re.compile(rule_regex)

	accounts = db.getCampaignAccounts(first_one.id, iterable_ret=False)

	# rootLogger.info(f"campaign accounts:{accounts}")

	my_redis = RedisWrapperClass()

	with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
		future_to_url = {executor.submit(processCampaignAccount, first_one, account, rule_regex, my_redis): account for account in accounts}
		# iterate through all
		for future in concurrent.futures.as_completed(future_to_url):
			account = future_to_url[future]

			if future.exception():
				formatted = traceback.format_tb(future.exception().__traceback__)
				new_line = "\n"
				rootLogger.error(f"Account[{account.id}] process:{future.exception()}")
				rootLogger.error(f"Account[{account.id}] process:{new_line}{''.join(formatted)}")
			else:
				rootLogger.info(f"Account[{account.id}] process: ok")



	# filter addresses
	# filtered_addresses = [item for item in addresses if not rule_regex.search( item.address )]
	# bad_addresses = [item for item in addresses if rule_regex.search( item.address )]
	# rootLogger.info(f"First campaign addresses:{[item.address for item in addresses]}")
	# rootLogger.info(f"First campaign addresses:{[item.address for item in filtered_addresses]}")
	# rootLogger.info(f"First campaign addresses filtered:{len(filtered_addresses)}")



