import MySQLdb
import itertools
import json
import re
import datetime
import time

from includes.RedisWrapperClass import RedisWrapperClass
from includes.MySQLWrapperClasses import MySQLWrapperClass, SQLAlchemyWrapperClass, SQLAlchemyBCWrapperClass
# import tables
from includes.tables.mail_accounts import mail_accounts
from includes.tables.mail_dump import mail_dump
from includes.tables.mail_account_addressbook import mail_account_addressbook
from includes.tables.campaign import campaign
from includes.tables.attachements import attachements
from includes.tables.attachement_campaign import attachement_campaign
from includes.tables.campaign_mail_accounts import campaign_mail_accounts
from includes.tables.scan_rules import scan_rules
from includes.tables.spam_base import spam_base
from includes.tables.spam_base_record import spam_base_record
from includes.tables.bc_socks import bc_socks
from includes.tables.mail_account_addresbook_maildump import mail_account_addresbook_maildump

from sqlalchemy import or_, and_, func, desc, asc, join
from sqlalchemy.sql.expression import bindparam
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.sql import select, text

from includes.RootLogger import rootLogger
import traceback
import mmh3
import binascii
import concurrent.futures

# import os
# from os.path import join, dirname
# from dotenv import load_dotenv
# # Create .env file path.
# dotenv_path = join(dirname(__file__), '.env')
# # Load file from the path.
# load_dotenv(dotenv_path)

#
# System settings
#
def getSystemSettings():
	def_results = {
		"socks_checker":{
			"number_process":10
		},
		"mail_grabber":{
			"number_process":20,
			"process_per_proxy":5,
			"partial":50,
			"max_mail_days_old":90
		},
		"campaign":{
			"max_active_campaigns":5,
			"workers_per_campaign":5,
			"connection_per_proxy":1,
			"cmp_check_interval":5,
			"reply_days": 30,
			# mark records as new(0)/skipped(4)/blacklisted(5), when no conversation found
			"reply_empty_status": 0,
			# 0 - only addressbook, 1 - only bases, 2 - use both adressbook + spambases
			"use_spambases": 0,
			# UTC 24hrs format
			"start_from": 10,
			"end_to": 16,
		},
		"acc_checker":{
			"min_hours": 2,
			"number_process": 20,
			"process_per_proxy": 5, #number of accounts per proxy
			"threads_per_protocol": 10, #when chek is started, maximum threads per protocol, so max connecttions per proxy: 3*process_per_proxy*threads_per_protocol
		},
	}

	# try to get from redis
	with RedisWrapperClass() as my_redis:
		results = my_redis.hgetall('settings')

	# if no try to get from database
	if bool(results) is False:
		with MySQLWrapperClass() as (db, cursor):
			sql = "SELECT * FROM system_settings"
			cursor.execute(sql)

			row = cursor.fetchone()

			# if no record, return empty dict
			if row is None:
				results = {}
			else:
				desc = cursor.description
				column_names = [col[0] for col in desc]

				result = dict(zip(column_names, row))

				json_str = result['settings']
				results = json.loads(json_str)

	else:
		results = {key: json.loads(results[key]) for key in results}

	no_ints = ('no-int-field', 'no-int-field2')
	# fill empty or missing properties form default
	for prop in def_results:
		if prop not in results:
			results[prop] = def_results[prop]
		else:
			for sub_prop in def_results[prop]:
				if sub_prop not in results[prop]:
					if sub_prop not in no_ints:
						results[prop][sub_prop] = int(def_results[prop][sub_prop])
					else:
						results[prop][sub_prop] = def_results[prop][sub_prop]
				else:
					if sub_prop not in no_ints:
						results[prop][sub_prop] = int(results[prop][sub_prop])
					else:
						results[prop][sub_prop] = results[prop][sub_prop]


	return results

def getDatabaseInstance():
	db_init = SQLAlchemyWrapperClass()
	return db_init.connection
#
# Socks check related functions
#
def getSocks(socks_type="spam", row_as_dict = False, alive_only = False, allow_smtp_only = False, enabled_only = True):
	# TODO: what is faster: inmemory requests in python or requests per item to redis?
	ret_socks = []
	with RedisWrapperClass() as my_redis:
		ret_socks = my_redis.hgetall('socks:data')
		# parse every row
		ret_socks = {skey: json.loads(ret_socks[skey]) for skey in ret_socks}

		if socks_type is not None:
			storage = 'socks:{}'.format(socks_type)
			ret_socks = {key: ret_socks[key] for key in ret_socks if int(my_redis.sismember(storage, key)) == 1}

		# apply alive filter
		if alive_only:
			storage = 'socks:alive'
			ret_socks = {key: ret_socks[key] for key in ret_socks if int(my_redis.sismember(storage, key)) == 1}

		# apply smtp_allow filter
		if allow_smtp_only:
			storage = 'socks:smtp'
			ret_socks = {key: ret_socks[key] for key in ret_socks if int(my_redis.sismember(storage, key)) == 1}

		# apply enabled filter
		if enabled_only:
			storage = 'socks:enabled'
			ret_socks = {key: ret_socks[key] for key in ret_socks if int(my_redis.sismember(storage, key)) == 1}

		# get hashses
		socks_banned = my_redis.hgetall('socks:banned')
		socks_hostname = my_redis.hgetall('socks:hostname')
		socks_outerip = my_redis.hgetall('socks:outerip')

		# append necesseary items
		for skey in ret_socks:
			ret_socks[skey]['id'] = skey

			if int(my_redis.sismember('socks:spam', skey)) == 1:
				ret_socks[skey]['type'] = 'spam'
			elif int(my_redis.sismember('socks:grabber', skey)) == 1:
				ret_socks[skey]['type'] = 'grabber'
			elif int(my_redis.sismember('socks:checker', skey)) == 1:
				ret_socks[skey]['type'] = 'checker'
			else:
				ret_socks[skey]['type'] = 'unknown'

			# ret_socks[skey]['type'] = 'spam' if int(my_redis.sismember('socks:spam', skey)) == 1 else 'grabber'

			ret_socks[skey]['banlist'] = socks_banned[skey] if skey in socks_banned else ''
			ret_socks[skey]['hostname'] = socks_hostname[skey] if skey in socks_hostname else ''
			ret_socks[skey]['outer_ip'] = socks_outerip[skey] if skey in socks_outerip else ''
			ret_socks[skey]['enabled'] = 1 if int(my_redis.sismember('socks:enabled', skey)) == 1 else 0
			ret_socks[skey]['allow_smtp'] = 1 if int(my_redis.sismember('socks:smtp', skey)) == 1 else 0
			ret_socks[skey]['smtp_allow'] = ret_socks[skey]['allow_smtp']
			ret_socks[skey]['alive'] = 1 if int(my_redis.sismember('socks:alive', skey)) == 1 else 0
			checked = my_redis.zscore('socks:checked', skey)
			ret_socks[skey]['checked_at'] = datetime.datetime.fromtimestamp( int(checked) if checked is not None else 0 )

		# dict to list
	return [ret_socks[skey] for skey in ret_socks]

def updateSocks(type="spam", socks = [], alive = 1, _reids=None):

	# TODO: maybe do it in one pipe?
	checked_at = int(datetime.datetime.now().timestamp())
	if _reids is None:
		my_redis = RedisWrapperClass()
	else:
		my_redis = _reids

	for item in socks:
		fails = 0
		if item['alive'] in (1, True):
			my_redis.sadd('socks:alive', item['id'])
			my_redis.srem('socks:dead', item['id'])
			my_redis.hset('socks:fails', item['id'], fails)
		else:
			my_redis.srem('socks:alive', item['id'])
			my_redis.sadd('socks:dead', item['id'])
			fails = my_redis.hincrby('socks:fails', item['id'], 1)

		if item['enabled'] in (1, True):
			my_redis.sadd('socks:enabled', item['id'])
			my_redis.srem('socks:disabled', item['id'])
		else:
			my_redis.srem('socks:enabled', item['id'])
			my_redis.sadd('socks:disabled', item['id'])

		if item['smtp_allow'] in (1, True) or item['allow_smtp'] in (1, True):
			my_redis.sadd('socks:smtp', item['id'])
		else:
			my_redis.srem('socks:smtp', item['id'])

		if len(item['banlist']) > 0:
			save_banlist = ''
			if isinstance(item['banlist'], str):
				save_banlist = item['banlist']
			else:
				save_banlist = ",".join(item['banlist'])

			# cut enything extra
			if len(save_banlist) > 256:
				save_banlist = save_banlist[:256]
			my_redis.hset('socks:banned', item['id'], save_banlist)
		else:
			my_redis.hdel('socks:banned', item['id'])

		if len(item['outer_ip']) > 0:
			my_redis.hset('socks:outerip', item['id'], item['outer_ip'])
		else:
			my_redis.hdel('socks:outerip', item['id'])

		if len(item['hostname']) > 0:
			my_redis.hset('socks:hostname', item['id'], item['hostname'])
		else:
			my_redis.hdel('socks:hostname', item['id'])

		# update checked at here...
		my_redis.zadd('socks:checked', {item['id']:checked_at} )

	return True

def removeFailedSocks(min_fails=5, _reids=None):
	if _reids is None:
		my_redis = RedisWrapperClass()
	else:
		my_redis = _reids

	failed_dict = my_redis.hgetall('socks:fails')
	failed_ids = []
	for sock_id, fails in failed_dict.items():
		if int(fails) > min_fails:
			failed_ids.append( {'id': sock_id} )

	# rootLogger.info(f"[Database] removeFailedSocks: got failed_ids:{failed_ids}")
	if len(failed_ids):
		removeSocks(failed_ids, my_redis)

def removeSocksJunkData(_reids):
	if _reids is None:
		my_redis = RedisWrapperClass()
	else:
		my_redis = _reids

	# remove any items NOT in socks:data
	leave_ids = my_redis.hkeys( 'socks:data' )
	remove_ids = []
	skeys = ('socks:alive', 'socks:dead', 'socks:enabled', 'socks:disabled', 'socks:grabber', 'socks:spam', 'socks:checker', 'socks:smtp')
	for set_key in skeys:
		tmp_ids = [sock_id for sock_id in my_redis.smembers(set_key) if sock_id not in leave_ids]
		remove_ids.extend( tmp_ids )

	remove_ids = set( remove_ids )
	# rootLogger.info(f"[Database] leave_ids:{leave_ids} vs remove_ids{remove_ids}")
	if len(remove_ids):
		with my_redis.pipeline() as pipe:
			for set_key in skeys:
				pipe.srem(set_key, *remove_ids)

			pipe.zrem("socks:checked", *remove_ids)
			# remove from hashes
			# pipe.hdel("socks:data", *remove_ids)
			pipe.hdel("socks:outerip", *remove_ids)
			pipe.hdel("socks:hostname", *remove_ids)
			pipe.hdel("socks:banned", *remove_ids)
			pipe.hdel("socks:fails", *remove_ids)

			pipe.execute()


def removeSocks(socks=[], _reids=None):
	if _reids is None:
		my_redis = RedisWrapperClass()
	else:
		my_redis = _reids

	# very dumb fuck, but who cares...
	for item in socks:
		my_redis.srem('socks:alive', item['id'])
		my_redis.srem('socks:dead', item['id'])
		my_redis.srem("socks:enabled", item['id'])
		my_redis.srem("socks:disabled", item['id'])
		my_redis.srem("socks:grabber", item['id'])
		my_redis.srem("socks:spam", item['id'])
		my_redis.srem("socks:checker", item['id'])
		my_redis.srem("socks:smtp", item['id'])
		my_redis.zrem("socks:checked", item['id'])
		# remove from hashes
		my_redis.hdel("socks:data", item['id'])
		my_redis.hdel("socks:outerip", item['id'])
		my_redis.hdel("socks:hostname", item['id'])
		my_redis.hdel("socks:banned", item['id'])
		my_redis.hdel("socks:fails", item['id'])

def getBCSocks():
	result = []
	try:
		with SQLAlchemyBCWrapperClass() as conn:
			query = select([bc_socks.c.addr]).select_from( bc_socks ).where(bc_socks.c.type == 'S')
			# result = conn.execute("select addr from ONLINE WHERE `type` = 'S'")
			result = conn.execute(query).fetchall()
	except Exception as e:
		rootLogger.error(f"[Database] getBCSocks: {e}")

	return result

def addSocks(socks=[], my_type='spam', _reids=None):
	if len(socks) < 1:
		return True

	if _reids is None:
		my_redis = RedisWrapperClass()
	else:
		my_redis = _reids

	existed_socks = my_redis.hkeys('socks:data')
	# rootLogger.info(f"[Database] addSocks: existed_socks:{existed_socks}")

	#
	with my_redis.pipeline() as pipe:

		#
		for item in socks:
			key_str = f"{item.addr}:{my_type}"
			skey = f"s:{binascii.crc32(key_str.encode())}"

			if skey in existed_socks:
				rootLogger.info(f"[Database] addSocks: allready existed id:{skey}, skip.")
				continue

			rootLogger.info(f"[Database] addSocks: new id:{skey}, insert.")

			#
			sddr_spl = item.addr.split(':')
			sdata = {'host': sddr_spl[0], 'port': int(sddr_spl[1]), 'login': '', 'password': '', 'type': my_type}

			# insert data into hash-map
			pipe.hset('socks:data', skey, json.dumps(sdata) )
			# insert key into few sets
			pipe.zadd('socks:checked', {skey: 0});
			# insert data into socks:types
			pipe.sadd(f"socks:{my_type}", skey);
			# insert data into alive
			pipe.sadd("socks:dead", skey);
			# insert data into enabled
			pipe.sadd("socks:enabled", skey);

		#
		pipe.execute()


def getTestAccounts(_conn=None):
	result = []
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			query = mail_accounts.select().where(mail_accounts.c.test_only == 1)
			result = conn.execute(query)
	except Exception as e:
		rootLogger.error(f"[Database] getTestAccounts: {e}")

	return result

#
# Thunderbird ISPDB data functions
#
def setDomainData(host, dict_val, my_redis=None):
	# save to redis
	if my_redis is None:
		my_redis = RedisWrapperClass()

	my_redis.set(f"isp:domain:{host}", json.dumps(dict_val))

def getDomainData(host, my_redis=None):
	res = None
	# with RedisWrapperClass() as my_redis:

	if my_redis is None:
		my_redis = RedisWrapperClass()

	redis_res = my_redis.get(f"isp:domain:{host}")
	if redis_res:
		res = json.loads(redis_res)

	return res

#
# Accounts check functions
#
def getCheckAccounts(hours_delta=3, _conn=None):
	current_time = datetime.datetime.utcnow()
	hours_ago = current_time - datetime.timedelta(hours=hours_delta)
	result = []
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			query = mail_accounts.select()\
					.where( or_ (mail_accounts.c.check_immediate == 1, mail_accounts.c.checked_at == None, mail_accounts.c.checked_at < hours_ago) )\
					.where(mail_accounts.c.need_grab_emails != 3)\
					.order_by(desc(mail_accounts.c.check_immediate), asc(mail_accounts.c.checked_at))
					# .where(mail_accounts.c.need_grab_emails != 0)\
			# rootLogger.info(f"getCheckAccounts query:{query}, hours_ago:{hours_ago}")
			result = conn.execute(query)

	except Exception as e:
		rootLogger.error(f"[Database] getCheckAccounts: {e}")

	return result

def setCheckAccounts(accounts, _conn=None):
	current_time = datetime.datetime.utcnow()

	# rootLogger.info(f"db.setCheckAccounts:{accounts}")

	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			query = mail_accounts.update()\
					.where(mail_accounts.c.id == bindparam('_id'))\
					.values({
						'smtp_host': bindparam('smtp_host'),
						'smtp_port': bindparam('smtp_port'),
						'smtp_login': bindparam('smtp_login'),
						'smtp_password': bindparam('smtp_password'),
						'smtp_ssl': bindparam('smtp_ssl'),
						'smtp_starttls': bindparam('smtp_starttls'),
						'smtp_alive': bindparam('smtp_alive'),

						'pop3_host': bindparam('pop3_host'),
						'pop3_port': bindparam('pop3_port'),
						'pop3_login': bindparam('pop3_login'),
						'pop3_password': bindparam('pop3_password'),
						'pop3_ssl': bindparam('pop3_ssl'),
						'pop3_alive': bindparam('pop3_alive'),

						'imap_host': bindparam('imap_host'),
						'imap_port': bindparam('imap_port'),
						'imap_login': bindparam('imap_login'),
						'imap_password': bindparam('imap_password'),
						'imap_ssl': bindparam('imap_ssl'),
						'imap_alive': bindparam('imap_alive'),

						'alive': bindparam('alive'),
						'web_alive': bindparam('web_alive'),
						'has_errors': bindparam('has_errors'),
						'error_log': bindparam('error_log'),
						'error_at': bindparam('error_at'),
						'checked_at': current_time,
						'updated_at': current_time,
						'check_immediate': 0,
						'need_grab_emails': bindparam('need_grab_emails'),
						'enabled': bindparam('enabled'),
					})

			result = conn.execute(query, accounts)
	except Exception as e:
		rootLogger.error(f"[Database] setCheckAccounts: {e}")
		# pass

	return True

#
# Mail grabber functions
#
def getGrabbingAccounts(days_delta=90, _conn=None):
	result = []
	# current_time = datetime.datetime.utcnow()
	# days_ago = current_time - datetime.timedelta(days=days_delta)
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:

			# no joins - because when dumps are over 1M, query might take etternety to complete...
			stmt = mail_accounts.select().\
				where(mail_accounts.c.enabled == 1).\
				where(mail_accounts.c.need_grab_emails == 1).\
				where( or_ (mail_accounts.c.pop3_alive == 1, mail_accounts.c.imap_alive == 1, mail_accounts.c.web_alive == 1))

			# this query deprecated and too colmplex, i guess the only flag i really need to use is '[protocol]_alive' and 'need_grab'

			# # substatement
			# subquery = select([mail_accounts.c.id.distinct()]).\
			# select_from(
			# 	mail_accounts.join(mail_dump, mail_dump.c.mail_account_id == mail_accounts.c.id)
			# ).\
			# where(mail_accounts.c.enabled == 1).\
			# where(mail_accounts.c.intersept == 0).\
			# where(mail_dump.c.body == '').\
			# where(mail_dump.c.mail_date > days_ago).\
			# order_by(desc(mail_accounts.c.id) )

			# # rootLogger.info(f"[Database]  getGrabbingAccounts subquery:{subquery}")

			# # common statement
			# colums = [
			# 	mail_accounts.c.id,

			# 	mail_accounts.c.pop3_alive,
			# 	mail_accounts.c.pop3_host,
			# 	mail_accounts.c.pop3_port,
			# 	mail_accounts.c.pop3_login,
			# 	mail_accounts.c.pop3_password,
			# 	mail_accounts.c.pop3_ssl,

			# 	mail_accounts.c.imap_alive,
			# 	mail_accounts.c.imap_host,
			# 	mail_accounts.c.imap_port,
			# 	mail_accounts.c.imap_login,
			# 	mail_accounts.c.imap_password,
			# 	mail_accounts.c.imap_ssl,

			# 	mail_accounts.c.enabled,
			# 	mail_accounts.c.alive,

			# 	mail_accounts.c.test_only,
			# 	mail_accounts.c.mail_dumps,
			# 	mail_accounts.c.addresses,

			# 	# no reason in column i guess
			# 	func.count(mail_accounts.c.id).label('mails'),
			# ]

			# tbl_join = mail_accounts.outerjoin(mail_account_addressbook,
   #			  mail_accounts.c.id == mail_account_addressbook.c.email_account_id)

			# agreg = select(colums).\
			# 		select_from(tbl_join).\
			# 		where(mail_accounts.c.enabled == 1).\
			# 		where(mail_accounts.c.need_grab_emails == 1).\
			# 		where(mail_accounts.c.intersept == 0).\
			# 		where( or_ (mail_accounts.c.pop3_alive == 1, mail_accounts.c.imap_alive == 1)).\
			# 		group_by( mail_accounts.c.id ).\
			# 		alias('agreg')

			# # where(mail_accounts.c.has_errors == 0).\ # no reason in this check, imap and pop are checked allready

			# # need another squlevel for quering because we migh choose betwen agregation (cont id) and id
			# stmt = select([agreg]).\
			# 		select_from(agreg).\
			# 		where( or_( agreg.c.mails < 1, agreg.c.id.in_(subquery)))

			# rootLogger.info(f"[Database]  getGrabbingAccounts query:{stmt}")
			# query = mail_accounts.select()

			# result = conn.execute(stmt)
			_result = conn.execute(stmt)
			result = _result.fetchall()
	except Exception as e:
		rootLogger.error(f"[Database] getGrabbingAccount: {e}")
		result = []

	return result

def getLatestMailDumpForEmailAccount(mail_account_id, _conn=None):
	result = None
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			stmt = select([
						mail_dump.c.id,
						func.max(mail_dump.c.mail_date).label('mail_date'),
						mail_dump.c.fp_crc
					]).\
					select_from(mail_dump).\
					where(mail_dump.c.mail_account_id == mail_account_id).\
					group_by(mail_dump.c.mail_account_id).\
					limit(1)

			# rootLogger.info(f"[Database] getLatestMailDumpForEmailAccount: {stmt}")
			result = conn.execute(stmt)
			if result is not None:
				result = result.fetchone()
				# rootLogger.info(f"[Database] getLatestMailDumpForEmailAccount result {result}")
	except Exception as e:
		rootLogger.error(f"[Database] getLatestMailDumpForEmailAccount: {traceback.format_exc()}")
		result = None

	return result

def getLatestMailDump(_conn=None):
	result = None
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			stmt = mail_dump.select().\
					order_by(desc(mail_dump.c.mail_date)).\
					limit(1)

			# rootLogger.info(f"[Database] getLatestMailDump: {stmt}")
			result = conn.execute(stmt)
			if result is not None:
				result = result.fetchone()
				# rootLogger.info(f"[Database] getLatestMailDump result {result}")
	except Exception as e:
		rootLogger.error(f"[Database] getLatestMailDump: {traceback.format_exc()}")
		result = None

	return result

def getLatestSpamBaseRecord(_conn=None):
	result = None
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			stmt = spam_base_record.select().\
					order_by(desc(spam_base_record.c.created_at)).\
					limit(1)

			# rootLogger.info(f"[Database] getLatestSpamBaseRecord: {stmt}")
			result = conn.execute(stmt)
			if result is not None:
				result = result.fetchone()
				# rootLogger.info(f"[Database] getLatestSpamBaseRecord result {result}")
	except Exception as e:
		rootLogger.error(f"[Database] getLatestSpamBaseRecord: {traceback.format_exc()}")
		result = None

	return result


# def updateMailAccount(mail_account_id, params, _conn=None):
# 	current_time = datetime.datetime.utcnow()
# 	params['updated_at'] = current_time
# 	# rootLogger.info(f"db.setCheckAccounts:{accounts}")
# 	try:
# 		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
# 			query = mail_accounts.update()\
# 					.where(mail_accounts.c.id == mail_account_id)\
# 					.values(params)

# 			result = conn.execute(query)
# 	except Exception as e:
# 		rootLogger.error(f"[Database] updateMailccount: {e}")
# 		# pass

# 	return True

def saveMailGrabberData(mail_dumps, addressbooks, accounts, _conn=None):
	current_time = datetime.datetime.utcnow()

	# save only dumps with body
	# mail_dumps = [item for item in mail_dumps if len(item['body']) > 0]

	# params['updated_at'] = current_time
	# rootLogger.info(f"db.setCheckAccounts:{accounts}")
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:


			if len(mail_dumps) > 0:
				query = mail_dump.insert().prefix_with("IGNORE")\
						.values({
							'mail_account_id': bindparam('mail_account_id'),
							'headers': bindparam('headers'),
							'from': bindparam('from'),
							'to': bindparam('to'),
							'subject': bindparam('subject'),
							'body': bindparam('body'),
							'msg_num': bindparam('msg_num'),
							'folder_path': bindparam('folder_path'),
							'need_body': 0,
							'has_attaches': bindparam('has_attaches'),
							'attach_path': bindparam('attach_path'),
							'mail_date': bindparam('mail_date'),
							'fp_crc': bindparam('fp_crc'),
							'is_spam': bindparam('is_spam'),
						})
						# .where(mail_dump.c.id == bindparam('_id'))\

				result = conn.execute(query, mail_dumps)

			if len(addressbooks) > 0:
				query = mail_account_addressbook.insert().prefix_with("IGNORE")\
						.values({
							'email_account_id': bindparam('email_account_id'),
							'address': bindparam('address'),
							'name': bindparam('name'),
							'company': '',
							'rest': '',
							'send_rule_id': None,
							'created_at': current_time,
							'updated_at': None
						})
						# .where(mail_dump.c.id == bindparam('_id'))\

				result = conn.execute(query, addressbooks)

			if len(accounts) > 0:
				# recalc addresses and get precalced dumps for accounts
				query = mail_accounts.update()\
						.where(mail_accounts.c.id == bindparam('_id'))\
						.values({
							'addresses': text('(SELECT COUNT(id) FROM mail_account_addressbook WHERE email_account_id = :_id)'),
							'mail_dumps': bindparam('mail_dumps'),
						})

				result = conn.execute(query, accounts)

			# now for every addressbook->account and binding to mail_dump
			# for dump in mail_dumps:
			# 	# addresses = ",".join( dump['from'], dump['to']).split(',')
			# 	# found addressbook item in dump
			# 	for item in addressbooks:
			# 		if item['address'] in f"{dump['from']}, {dump['to']}":

			# 			# search id for particular address
			# 			query = mail_account_addressbook.select()\
			# 					.where(mail_account_addressbook.c.address == item['address'])
			# 					.where(mail_account_addressbook.c.email_account_id == dump['mail_account_id'])

			# 			result_addressbook = None
			# 			try:
			# 				result_addressbook = conn.execute(query).fetchone()
			# 			except Exception as e:
			# 				pass

			# 			query = mail_dump.select()\
			# 						.where( mail_dump.c.fp_crc == dump['fp_crc'] )\
			# 						.where( mail_dump.c.mail_account_id == dump['mail_account_id'] )\
			# 						.where( mail_dump.c.msg_num == dump['msg_num'] )

			# 			result_dump = None
			# 			try:
			# 				result_dump = conn.execute(query).fetchone()
			# 			except Exception as e:
			# 				pass

			# 			# do nothing if we can't do anything
			# 			if result_addressbook is None or result_dump  is None:
			# 				continue

			# 			# insert if good
			# 			query = mail_account_addresbook_maildump.insert().values(
			# 				addressbook_id = result_addressbook.id,
			# 			    mail_account_id = result_dump.mail_account_id,
			# 			    mail_dump_id = result_dump.id,
			# 			)

			# 			try:
			# 				result = conn.execute(query)
			# 			except Exception as e:
			# 				pass
			# 			# finally:
			# 			# 	break



	except Exception as e:
		# {traceback.format_exc()}
		rootLogger.error(f"[Database] saveMailGrabberData: {e}")
		# pass

	return True

def updateMailAccounts(accounts, recalc_values=False, _conn=None):
	current_time = datetime.datetime.utcnow()

	if len(accounts) < 1:
		return True

	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			query = mail_accounts.update()\
					.where(mail_accounts.c.id == bindparam('_id'))\
					.values({
						key: bindparam(key) for key in accounts[0] if key not in ('updated_at', '_id', 'created_at')
						# 'need_grab_emails': bindparam('need_grab_emails'),
						# 'all_names': bindparam('all_names'),

						# 'has_errors': bindparam('has_errors'),
						# 'error_log': bindparam('error_log'),
						# 'error_at': bindparam('error_at'),
						# 'updated_at': current_time,
					})

			result = conn.execute(query, accounts)

			# also recalc
			if recalc_values:
				query = mail_accounts.update()\
						.where(mail_accounts.c.id == bindparam('_id'))\
						.values({
							'addresses': text('(SELECT COUNT(id) FROM mail_account_addressbook WHERE email_account_id = :_id)'),
							'mail_dumps': text('(SELECT COUNT(id) FROM mail_dump WHERE mail_account_id = :_id)'),
						})

			result = conn.execute(query, accounts)

	except Exception as e:
		rootLogger.error(f"[Database] updateMailAccounts: {e}")
		# pass

	return True

#
# SMTP sendings functions
#
def getCampaigns(status=0, name=None, _id=None, _conn=None):
	current_time = datetime.datetime.utcnow()
	result = []
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			query = campaign.select()\
					.order_by(desc(campaign.c.updated_at))

			#
			if status is not None:
				query = query.where(campaign.c.status == status)

			if name is not None:
				query = query.where(campaign.c.name == name)

			if _id is not None:
				query = query.where(campaign.c.id == _id)

			result = conn.execute(query)

	except Exception as e:
		rootLogger.error(f"[Database] getCampaigns: {e}")

	return result

def createCampaign(
		status=0,
		title='universalio',
		subject='',
		body="[%%ML_ANSWER%%]",
		is_html=1,
		headers={},
		account_name='',
		filters='robots,still_in_progress,yahoo,aol,av,the_rest_big,big_banks_in_progress,social,google,microsoft,shops_etc,euro_zones,bad_zones,general',
		attach_name="[\%\%Detailed|Copy|Scan|Reports|Information|Documentation|Note|Notice|Notification\%\%][\%\%-|_|.\%\%][%ORandStr%4-9,0-9,R,1\%\%].doc",
		_conn=None,
	):

	query = campaign.insert().values(
		name=title,
		subject=subject,
		body=body,
		is_html=is_html,
		headers=json.dumps(headers),
		account_name=account_name,
		max_messages=0,
		per_time=0,
		ignore_selfhost=0,
		reply_mode=1,
		reply_days=30,
		status=status,
		workers=0,
		total_emails=0,
		created_at=datetime.datetime.utcnow(),
		updated_at=None,
		scheduled_to=None,
		scheduled=None,
		started_at=datetime.datetime.utcnow(),
		finnished_at=None,
		filters=filters,
		attach_name=attach_name,
		ignore_accounts=0,
		fail_behaviour=0,
		check_send=0,
		has_attaches=1,
	)

	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			result = conn.execute(query)

	except Exception as e:
		rootLogger.error(f"[Database] createCampaign: {e}")
		# pass

	return True


def updateCampaigns(records, _conn=None):
	# current_time = datetime.datetime.utcnow()

	if len(records) < 1:
		return True

	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			query = campaign.update()\
					.where(campaign.c.id == bindparam('_id'))\
					.values({
						key: bindparam(key) for key in records[0] if key not in ('_id', 'created_at')
					})

			result = conn.execute(query, records)

	except Exception as e:
		rootLogger.error(f"[Database] updateCampaigns: {e}")
		# pass

	return True

def getCampaignAttachements(cmp_id, _conn=None):

	my_join = attachement_campaign.join(attachements, attachements.c.id == attachement_campaign.c.attachement_id)

	query = select([
			attachements.c.id,
			attachements.c.data,
			attachements.c.name,
		attachements.c.used]).\
		select_from( my_join ).\
		where(attachement_campaign.c.campaign_id == cmp_id)

	# rootLogger.info(f"[Database] getCampaignAttachements query:{query}")

	result = []
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			result = conn.execute(query)
	except Exception as e:
		rootLogger.error(f"[Database] getCampaignAttachements({cmp_id}): {e}")

	return result

def updateCampaignAttachements(records, _conn=None):
	current_time = datetime.datetime.utcnow()

	if len(records) < 1:
		return True

	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			query = attachements.update()\
					.where(attachements.c.id == bindparam('_id'))\
					.values({
						key: bindparam(key) for key in records[0] if key not in ('_id', 'created_at')
					})

			result = conn.execute(query, records)

	except Exception as e:
		rootLogger.error(f"[Database] updateCampaignAttachements: {e}")
		# pass

	return True

def insertCampaignAttachement(binary_data, camp_id, _group='universalio', _conn=None):
	now = datetime.datetime.utcnow()
	doc_name = f'{now}.doc'.replace(' ', '_'),
	query = attachements.insert().values(
		name=doc_name,
		campaign_id=0,
		size=len(binary_data),
		path=doc_name,
		data=binary_data,
		group=_group,
		used=0,
		created_at=text(f"NOW()"),
		updated_at=None,
	)

	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			result = conn.execute(query, records)
	except Exception as e:
		rootLogger.error(f"[Database] insertCampaignAttachement insert: {e}")
		return None

	# get  current document
	document = None
	query = select().select_from(attachements).where(attachements.c.name == doc_name)
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			document = conn.execute(query, records).fetchone()
	except Exception as e:
		rootLogger.error(f"[Database] insertCampaignAttachement select: {e}")
		return None

	# if no document, return
	if not document:
		rootLogger.error(f"[Database] insertCampaignAttachement select document with name:{doc_name} not found.")
		return None

	query = attachement_campaign.insert().values(
		campaign_id=camp_id,
		attachement_id=document.id
	)

	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			result = conn.execute(query, records)
	except Exception as e:
		rootLogger.error(f"[Database] insertCampaignAttachement insert: {e}")

	return None

def getMacroTemplates(my_redis=None):
	if my_redis is None:
		my_redis = RedisWrapperClass()

	results = my_redis.hgetall('macro:data')
	return results

def getCampaignAccounts(cmp_id=None, iterable_ret=True, _conn=None):

	if cmp_id is None:
		return []

	my_join = campaign_mail_accounts.join(mail_accounts, mail_accounts.c.id == campaign_mail_accounts.c.mail_account_id)

	query = select([mail_accounts]).\
		select_from( my_join ).\
		where(campaign_mail_accounts.c.campaign_id == cmp_id)

	# rootLogger.info(f"[Database] getCampaignAccounts query:{query}")

	result = []
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			_result = conn.execute(query)
			if not iterable_ret:
				result = _result.fetchall()
			else:
				result = _result
	except Exception as e:
		rootLogger.error(f"[Database] getCampaignAccounts({cmp_id}): {e}")

	return result

def getAutomaticSpamBases(iterable_ret=False, _conn=None):

	query = spam_base.select().where( spam_base.c.enable_automatics > 0 )

	# rootLogger.info(f"[Database] getCampaignAccounts query:{query}")

	result = []
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			_result = conn.execute(query)
			if not iterable_ret:
				result = _result.fetchall()
			else:
				result = _result
	except Exception as e:
		rootLogger.error(f"[Database] getAutomaticSpamBases: {e}")

	return result

def getSpamBaseRecords(base=None, offset=0, limit=1000, iterable_ret=False, _conn=None):
	if base is None:
		return []

	query = select([
		spam_base_record.c.id.label('spam_base_record_id'),
		spam_base_record.c.address,
		spam_base_record.c.name,
		spam_base_record.c.company,
		spam_base_record.c.rest,
		spam_base_record.c.spam_base_id,
		# spam_base_record.c.email_account_id,
		# spam_base_record.c.mail_account_addressbook_id,

	]).select_from( spam_base_record ).where( spam_base_record.c.spam_base_id == base.id ).offset( offset ).limit( limit )

	result = []
	try:
		with SQLAlchemyWrapperClass(_conn=None) as conn:
			_result = conn.execute(query)
			if not iterable_ret:
				result = _result.fetchall()
			else:
				result = _result
	except Exception as e:
		rootLogger.error(f"[Database] getSpamBaseRecords({base.id}): {e}")

	return result

def getCampaignRecord(camp_id, mac_id, try_empty=True, move_from=0, move_to=0, my_redis=None):
	if my_redis is None:
		my_redis = RedisWrapperClass()

	skey = "campaign:{}:account:{}:records:{}".format(camp_id, mac_id, move_from)
	record_id = my_redis.spop(skey)
	# print("try: {}".format(skey))

	# when empty, try none list
	if record_id is None and try_empty:
		mac_id = 'none'
		skey = "campaign:{}:account:{}:records:{}".format(camp_id, mac_id, move_from)
		record_id = my_redis.spop(skey)

	# if empty, quit
	if record_id is None:
		return None

	# get proper data from redis
	data = my_redis.hgetall(record_id)
	# for ease of use
	data['id'] = record_id

	my_redis.hset(record_id, "record_status", move_to)

	# print("move_from:{}, move_to:{}".format(move_from, move_to))
	# move from one list to another
	from_key = "campaign:{}:records:{}".format(camp_id, move_from)
	to_key = "campaign:{}:records:{}".format(camp_id, move_to)
	# print("{} moved from {} to {}".format(record_id, from_key, to_key))
	# my_redis.lrem(from_key, 0, record_id)
	my_redis.srem(from_key, record_id)
	# my_redis.lpush(to_key, record_id)
	my_redis.sadd(to_key, record_id)

	# move this record to pocessings
	from_key = "campaign:{}:account:{}:records:{}".format(camp_id, mac_id, move_from)
	to_key = "campaign:{}:account:{}:records:{}".format(camp_id, mac_id, move_to)

	# print("smove {} {} {}".format(from_key, to_key, record_id))
	# my_redis.smove(from_key, to_key, record_id)
	my_redis.srem(from_key, record_id)
	my_redis.sadd(to_key, record_id)

	return data

def getCampaignRecords(camp_id, record_status=0, my_redis=None):
	if my_redis is None:
		my_redis = RedisWrapperClass()

	list_key = "campaign:{}:records:{}".format(camp_id, record_status)

	# res = my_redis.lrange(list_key, 0, -1)
	res = my_redis.smembers(list_key)
	return res

def updateCampaignRecord(record, my_redis=None):
	key = record.pop('id', None)
	if key is None:
		return None

	if my_redis is None:
		my_redis = RedisWrapperClass()

	camp_id = record['campaign_id']
	mac_id = record['mail_account_id'] if len(record['mail_account_id']) > 0 else 'none'
	status = record['record_status']
	# update data
	# print("updateCampaignRecord:{}\n{}".format(key, record))
	my_redis.hmset(key, record)
	# remove it from all status types
	for idx in range(10):
		skey = "campaign:{}:records:{}".format(camp_id, idx)
		# my_redis.lrem(skey, 0, key)
		my_redis.srem(skey, key)
		skey = "campaign:{}:account:{}:records:{}".format(camp_id, mac_id, idx)
		my_redis.srem(skey, key)

	# add to proper list and account set
	skey = "campaign:{}:records:{}".format(camp_id, status)
	# my_redis.rpush(skey, key)
	my_redis.sadd(skey, key)


	skey = "campaign:{}:account:{}:records:{}".format(camp_id, mac_id, status)
	my_redis.sadd(skey, key)

	return True

def changeCampaignRecordStatus(camp_id, old_status, new_status, my_redis=None):
	old_lkey = "campaign:{}:records:{}".format(camp_id, old_status)
	new_lkey = "campaign:{}:records:{}".format(camp_id, new_status)

	if my_redis is None:
		my_redis = RedisWrapperClass()

	# record = my_redis.lpop(old_lkey)
	record = my_redis.spop(old_lkey)
	while record:
		print("moving record:{} from {} to {}".format(record, old_status, new_status))
		rdata = my_redis.hgetall(record)
		mac_id = rdata["mail_account_id"]

		old_skey = "campaign:{}:account:{}:records:{}".format(camp_id, mac_id, old_status)
		new_skey = "campaign:{}:account:{}:records:{}".format(camp_id, mac_id, new_status)

		# update record data for account
		my_redis.hset(record, 'record_status', new_status)
		my_redis.sadd(new_skey, record)
		my_redis.srem(old_skey, record)
		# my_redis.smove(old_skey, new_skey, record)
		# print("smove {} {} {}".format(old_skey, new_skey, record))

		# my_redis.lrem(old_lkey, 0, record)
		my_redis.srem(old_lkey, record)
		# print("lrem {} {} {}".format(old_lkey, 0, record))

		# my_redis.lrem(new_lkey, 0, record)
		my_redis.srem(new_lkey, record)
		# print("lrem {} {} {}".format(new_lkey, 0, record))

		# my_redis.rpush(new_lkey, record)
		my_redis.sadd(new_lkey, record)
		# print("rpush {} {}".format(new_lkey, record))

		# get new record from database
		# record = my_redis.lpop(old_lkey)
		record = my_redis.spop(old_lkey)

def moveCampaignRecords(camp_id, old_mac, new_mac, status=0, records=[], my_redis=None):
	old_skey = "campaign:{}:account:{}:records:{}".format(camp_id, old_mac, status)
	new_skey = "campaign:{}:account:{}:records:{}".format(camp_id, new_mac, status)

	if my_redis is None:
		my_redis = RedisWrapperClass()
	# if no records specified, move all
	if len(records) < 1:
		records = my_redis.smembers(old_skey)

	for record_id in records:
		my_redis.sadd(new_skey, record_id)
		my_redis.srem(old_skey, record_id)

		# get old status, move from old status to new status
		# old_status = my_redis.hset(record_id, "record_status")
		old_status = my_redis.hget(record_id, "record_status")
		old_lkey = "campaign:{}:records:{}".format(camp_id, old_status)
		new_lkey = "campaign:{}:records:{}".format(camp_id, status)

		# my_redis.lrem(old_lkey, 0, record_id)
		my_redis.srem(old_lkey, record_id)
		# my_redis.lrem(new_lkey, 0, record_id)
		my_redis.srem(new_lkey, record_id)
		# my_redis.rpush(new_lkey, record_id)
		my_redis.sadd(new_lkey, record_id)

		# update record data
		if new_mac == 'none':
			my_redis.hset(record_id, "mail_account_id", "")
		else:
			my_redis.hset(record_id, "mail_account_id", new_mac)

	return True

# debug only
def changeAccountRecordsStatus(camp_id, mac_id, old_status=0, new_status=0, records=[], my_redis=None):
	old_skey = "campaign:{}:account:{}:records:{}".format(camp_id, mac_id, old_status)
	new_skey = "campaign:{}:account:{}:records:{}".format(camp_id, mac_id, new_status)

	old_lkey = "campaign:{}:records:{}".format(camp_id, old_status)
	new_lkey = "campaign:{}:records:{}".format(camp_id, new_status)

	# print(old_skey + "==>" + new_skey)
	# print(old_lkey + "==>" + new_lkey)

	if my_redis is None:
		my_redis = RedisWrapperClass()

	# if no records specified, move all
	if len(records) < 1:
		records = my_redis.smembers(old_skey)

	for item in records:
		my_redis.smove( old_skey, new_skey, item)
		# my_redis.lrem( old_lkey, 0, item)
		my_redis.srem( old_lkey, 0, item)
		# my_redis.lrem( new_lkey, 0, item)
		my_redis.srem( new_lkey, 0, item)
		# my_redis.rpush( new_lkey, item)
		my_redis.sadd( new_lkey, item)

	return True
# EOF: debug only

def removeCampaignRecords(camp_id, mac_id, status=None, records=[], my_redis=None, remove_from_list=True):
	if my_redis is None:
		my_redis = RedisWrapperClass()

	if status is None:
		skeys = ["campaign:{}:account:{}:records:{}".format(camp_id, mac_id, my_status) for my_status in (0,1,2,3,4,5)]
		lkeys = ["campaign:{}:records:{}".format(camp_id, my_status) for my_status in (0,1,2,3,4,5)]
	else:
		skeys = ["campaign:{}:account:{}:records:{}".format(camp_id, mac_id, status)]
		lkeys = ["campaign:{}:records:{}".format(camp_id, mac_id, status)]

	if len(records) < 1:
		for skey in skeys:
			# rootLogger.info(f"[Database] removeCampaignRecords[{camp_id}] extend items from:{skey}")
			records.extend( my_redis.smembers(skey) )

	# bulk removal
	if len(records) > 0:

		# split into smaller chunks
		max_size = 250
		chunked = [records[i:i+max_size] for i in range(0, len(records), max_size)]

		rootLogger.info(f"[Database] removeCampaignRecords[{camp_id}] for account:{mac_id}, total:{len(records)}")
		for records in chunked:
			with my_redis.pipeline() as pipe:

				if remove_from_list:
					# remove from account records set
					for skey in skeys:
						pipe.srem( skey, *records)

					for lkey in lkeys:
						pipe.srem( lkey, *records)

					# for item in records:
					# 	# rootLogger.info(f"[Database] removeCampaignRecords remove:{item}")

					# 	# remove from account records set
					# 	for lkey in lkeys:
					# 		pipe.lrem( lkey, 0, item)

				# remove items itself
				pipe.delete( *records )

				pipe.execute()
	else:
		rootLogger.info(f"[Database] removeCampaignRecords[{camp_id}] for account:{mac_id}, no records: {len(records)}")


	# clear just in case
	records=[]

def removeCampaign(camp_id, status=None, records=[], my_redis=None, my_workers=5, _conn=None):
	if my_redis is None:
		my_redis = RedisWrapperClass()

	# get all campaign accounts
	accs_key  = f"campaign:{camp_id}:accounts"

	# accounts list
	accs = my_redis.smembers( accs_key )
	mac_ids = [ acc_id.split(":")[3] for acc_id in accs]

	with concurrent.futures.ThreadPoolExecutor(max_workers=my_workers) as executor:

		future_to_url = {executor.submit(removeCampaignRecords, camp_id, mac_id, None, [], my_redis, False): mac_id for mac_id in mac_ids}

		for future in concurrent.futures.as_completed(future_to_url):
			mac_id = future_to_url[future]
			if future.exception():
				rootLogger.error(f"[Database] removeCampaign[{camp_id}][{mac_id}] fails:{future.exception()}")
				formatted = traceback.format_tb(future.exception().__traceback__)
				new_line = "\n"
				rootLogger.error(f"[Database] removeCampaign[{camp_id}][{mac_id}] {new_line}{''.join(formatted)}")
			else:
				res = future.result()
				rootLogger.info(f"[Database] removeCampaign[{camp_id}][{mac_id}]: account is done.")

				skeys = ["campaign:{}:account:{}:records:{}".format(camp_id, mac_id, my_status) for my_status in (0,1,2,3,4,5)]

				my_redis.delete( *skeys )

				# for skey in skeys:
				# 	my_redis.delete( skey )

	#
	# for acc_id in accs:
	# 	mac_id = acc_id.split(":")[3]
	# 	print(f"removing campaign:{camp_id} account:{mac_id}")

	# 	removeCampaignRecords( camp_id, mac_id, status=None, records=[], my_redis=my_redis )
	# 	# now remova all rest items
	# 	skeys = ["campaign:{}:account:{}:records:{}".format(camp_id, mac_id, my_status) for my_status in (0,1,2,3,4,5)]

	# 	for skey in skeys:
	# 		my_redis.delete( skey )

	# remove common records containsers
	rootLogger.info(f"[Database] removeCampaign[{camp_id}] common records containers")
	lkeys = ["campaign:{}:records:{}".format(camp_id, my_status) for my_status in (0,1,2,3,4,5)]
	for lkey in lkeys:
		my_redis.delete( lkey )

	#
	rootLogger.info(f"[Database] removeCampaign[{camp_id}] accounts container")
	my_redis.delete( accs_key )

	#
	rootLogger.info(f"[Database] removeCampaign[{camp_id}] accounts from database")
	query = campaign.delete().where( campaign.c.id == int(camp_id) )
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			_result = conn.execute(query)
	except Exception as e:
		rootLogger.error(f"[Database] removeCampaign({camp_id}): {e}")


def appendAccountsToCampaign(cmp_id, append_new=True, acc_ids=[], _conn=None):

	# extend acc_ids with
	if append_new:
		subquery = select( [campaign_mail_accounts.c.mail_account_id] ).select_from(campaign_mail_accounts).where( campaign_mail_accounts.c.campaign_id == cmp_id )
		# if append new, then check accounts not in campaign
		query = select( [ mail_accounts.c.id ])\
				.select_from( mail_accounts )\
				.where( ~mail_accounts.c.id.in_( subquery ) )\
				.where( mail_accounts.c.smtp_alive > 0 )\
				.where( mail_accounts.c.has_errors == 0 )\
				.where( mail_accounts.c.checked_at != None )

		try:
			with SQLAlchemyWrapperClass(_conn=_conn) as conn:
				_result = conn.execute(query)
				items = _result.fetchall()
				acc_ids.extend( [item.id for item in items] )
				# # make items unique
				acc_ids = list(set(acc_ids))
		except Exception as e:
			rootLogger.error(f"[Database] appendAccountsToCampaign on select campaign_mail_accounts: {e}")

	# no reason for connection if no accounts
	if len(acc_ids):
		try:
			with SQLAlchemyWrapperClass(_conn=_conn) as conn:
				query = campaign_mail_accounts.insert().\
							prefix_with("IGNORE").\
							values( [{'campaign_id':cmp_id, 'mail_account_id':acc_id} for acc_id in acc_ids] )

				conn.execute(query)
		except Exception as e:
			rootLogger.error(f"[Database] appendAccountsToCampaign on insert accounts: {e}")

	return True

def getCampaignAccountsAddresses(cmp_id=None, acc_ids=[], _conn=None):

	if cmp_id is None:
		return []

	if not len(acc_ids):
		query  = select( [campaign_mail_accounts.c.mail_account_id] )\
					.select_from( campaign_mail_accounts )\
					.where( campaign_mail_accounts.c.campaign_id == cmp_id )

		try:
			with SQLAlchemyWrapperClass(_conn=_conn) as conn:
				_result = conn.execute(query)
				items = _result.fetchall()
				acc_ids.extend( [item.mail_account_id for item in items] )
				acc_ids = list(set(acc_ids))
		except Exception as e:
			rootLogger.error(f"[Database] getCampaignAccountsAddresses on select campaign_mail_accounts.id: {e}")

	# rootLogger.info(f"[Database] getCampaignAccountsAddresses acc_ids:{acc_ids}")
	query = mail_account_addressbook.select().where( mail_account_addressbook.c.email_account_id.in_(acc_ids) )
	# rootLogger.info(f"[Database] getCampaignAccountsAddresses query:{query}")

	result = []
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			_result = conn.execute(query)
			result = _result.fetchall()
	except Exception as e:
		rootLogger.error(f"[Database] getCampaignAccountsAddresses on select mail_account_addressbook: {e}")

	return result

def getAccountAddressBook(acc_ids=[], _conn=None):
	query = mail_account_addressbook.select().where( mail_account_addressbook.c.email_account_id.in_(acc_ids) )
	result = []
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			_result = conn.execute(query)
			result = _result.fetchall()
	except Exception as e:
		rootLogger.error(f"[Database] getAccountAddressBook on select mail_account_addressbook: {e}")

	return result

def getAddressBookRecords(offset=0, limit=1000, _conn=None):
	query = shell_history.select()

	my_join = mail_accounts.join(mail_account_addressbook, mail_accounts.c.id == mail_account_addressbook.c.mail_account_id)

	query = select([
			mail_accounts.c.id,
			mail_accounts.c.name.label('account_name'),
			mail_accounts.c.smtp_login,
			mail_accounts.c.pop3_login,
			mail_accounts.c.imap_login,

			mail_account_addressbook.c.address,
			mail_account_addressbook.c.name,

		]).\
		select_from( my_join )


	# query = mail_account_addressbook.select().offset(offset).limit(limit)
	# result = []
	# try:
	# 	with SQLAlchemyWrapperClass(_conn=_conn) as conn:
	# 		_result = conn.execute(query)
	# 		result = _result.fetchall()
	# except Exception as e:
	# 	rootLogger.error(f"[Database] getAddressBookRecords on select mail_account_addressbook: {e}")

	# return result



def getAddressBookContactConversation(account, contact, max_days=90, _conn=None):
	query = select([mail_dump.c.subject, mail_dump.c.body, mail_dump.c.headers])\
		.select_from(mail_dump)\
		.where( mail_dump.c.mail_account_id == account.id )\
		.where( mail_dump.c.mail_date >= text(f"NOW() - INTERVAL {max_days} DAY") )\
		.where( or_(
			# getattr(mail_dump.c, 'from') == contact.address,
			mail_dump.c['from'].like('%' + contact.address + '%'),
			mail_dump.c.to.like('%' + contact.address + '%'),
		))\
		.order_by( desc(mail_dump.c.mail_date) )\
		.limit( 5 )

	# print(f"query:{query} dump.from:{contact.address}, mail_account_id:{account.id} max_days:{max_days}")

	result = []
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			_result = conn.execute(query)
			result = _result.fetchall()
	except Exception as e:
		rootLogger.error(f"[Database] getAddressBookContactConversation: {e}")

	return result

def getCampaignScanRules(groups=[], _conn=None):
	if isinstance(groups, str):
		groups = groups.split(',')

	query = select([scan_rules.c.rule, scan_rules.c.group]).where(scan_rules.c.enabled == 1).where( scan_rules.c.group.in_( groups ) )

	result = []
	try:
		with SQLAlchemyWrapperClass(_conn=_conn) as conn:
			_result = conn.execute(query)
			if _result.rowcount > 0:
				result = _result.fetchall()
	except Exception as e:
		rootLogger.error(f"[Database] getCampaignScanRules on select mail_account_addressbook: {e}")

	return result

def getCommonLogin(account):
	if account is None:
		return 'none'

	if not account.web_login:
		login = account.web_login;
	elif not account.smtp_login:
		login = account.smtp_login;
	elif  not account.pop3_login:
		login = account.pop3_login;
	elif  not account.imap_login:
		login = account.imap_login;

	return login

def getCampaignRecordStatus(camp_id, mac_id, record_id='', my_redis=None, exclude_status=-1):
	if my_redis is None:
		my_redis = RedisWrapperClass()

	ret = -1

	from includes.SMTPThread import RS_NEW, RS_PROCESSING, RS_SUCCESS, RS_FAILED, RS_SKIPPED, RS_BLACKLIST
	all_statuses = (RS_NEW, RS_PROCESSING, RS_SUCCESS, RS_FAILED, RS_SKIPPED, RS_BLACKLIST)

	# search in all statuses
	for status in all_statuses:
		# skip status
		if status == exclude_status:
			continue

		skey = "campaign:{}:account:{}:records:{}".format(camp_id, mac_id, status)
		if int(my_redis.sismember(skey, record_id)) == 1:
			ret = status
			break

	return ret

def putRecordsToRedis(campaign, mail_account=None, records=[], record_status=-1, record_status_txt='', my_redis=None, override_status=False):
	if my_redis is None:
		my_redis = RedisWrapperClass()

	from includes.SMTPThread import RS_NEW, RS_PROCESSING, RS_SUCCESS, RS_FAILED, RS_SKIPPED, RS_BLACKLIST

	all_statuses = (RS_NEW, RS_PROCESSING, RS_SUCCESS, RS_FAILED, RS_SKIPPED, RS_BLACKLIST)
	await_status = RS_NEW

	if record_status < await_status:
		record_status = await_status


	# check for mail_account_id
	if mail_account:
		mac_id = mail_account.id
	else:
		mac_id = 'none'

	# SET key
	existed_records = []
	for my_status in all_statuses:
		iter_acc_set_key = f"campaign:{campaign.id}:account:{mac_id}:records:{my_status}"
		existed_records.extend( my_redis.smembers(iter_acc_set_key) )

	acc_set_key = f"campaign:{campaign.id}:account:{mac_id}:records:{record_status}"
	list_key = f"campaign:{campaign.id}:records:{record_status}"


	mail_accs_key = f"campaign:{campaign.id}:accounts"

	from_mail = getCommonLogin( mail_account )
	from_name = 'none'
	if len( getattr(mail_account, 'name', '')):
		from_name = mail_account.name

	spambase_key = f"campaign:{campaign.id}:spambases"
	# expire after 30 days
	expire_time = 3600*24*30;

	# rootLogger.info(f"[Database] putRecordsToRedis: acc_set_key:{acc_set_key}, list_key:{list_key}, records:{len(records)}, override_status:{override_status}")


	# bulk insertion
	with my_redis.pipeline() as pipe:

		for record in records:
			# hash_id = hex(mmh3.hash(f'{campaign.id}{from_mail}{from_name}') & 0xffffffff)[2:]
			# $hash_id = Murmur::hash3("{$campaign_id}{$from_mail}{$from_name}" . $item->address );
			hash_id = hex(mmh3.hash64(f"{campaign.id}{from_mail}{from_name}{record['address']}")[0] & 0xffffffffffffffff)[2:]
			hash_key = f"campaign:{campaign.id}:record:{hash_id}"
			# rootLogger.info()

			if hash_key in existed_records:
				# just skip allready existed
				if not override_status:
					continue

				# remove from other lists and apply to current
				for my_status in all_statuses:
					if my_status != record_status:
						pipe.srem( f"campaign:{campaign.id}:account:{mac_id}:records:{my_status}",  hash_key)
						# pipe.lrem( f"campaign:{campaign.id}:records:{my_status}", 0, hash_key)
						pipe.srem( f"campaign:{campaign.id}:records:{my_status}", hash_key)

			# save hash key for futher iterations
			record['hash_key'] = hash_key

			# save item itself
			pipe.hmset(hash_key, record)
			# set expire status to clear data
			pipe.expire(hash_key, expire_time)
			# per account, so pop it in python
			pipe.sadd(acc_set_key, hash_key)
			# common list
			# pipe.rpush(list_key, hash_key);
			pipe.sadd(list_key, hash_key);

			# spam bases set
			if 'spam_base_id' in record and record['spam_base_id'] != '':
				pipe.sadd(spambase_key, record['spam_base_id'])

			pipe.sadd(mail_accs_key, acc_set_key)

		pipe.execute()

	# my_redis.lrem(list_key, 0, hash_key)

	# Redis::pipeline(function (pipe) use (campaign_id, mail_account.id, records, list_key, from_mail, from_name, record_status, record_status_txt, acc_set_key, mail_accs_key, expire_time, spambase_key) {
	# 	foreach (records as item) {
	# 		if( is_array(item) ){
	# 			# check if it's blacklist item where [item, blacklist]
	# 			if ( array_key_exists(1, item) ){
	# 				record_status_txt = item[1];
	# 				if( is_array(item[0]))
	# 					item = (object)item[0];
	# 				else
	# 					item = item[0];
	# 			} elseif ( array_key_exists('1', item) ){
	# 				record_status_txt = item['1'];
	# 				if( is_array(item['0']))
	# 					item = (object)item['0'];
	# 				else
	# 					item = item['0'];
	# 			} else {
	# 				item = (object)item;
	# 			}
	# 		}

	# 		if( !property_exists(item, 'address') ){
	# 			\Log::debug("Item has no address:" . json_encode(item));
	# 			continue;
	# 		}

	# 		hash_id = Murmur::hash3("{campaign_id}{from_mail}{from_name}" . item->address );
	# 		hash_key = "campaign:{campaign_id}:record:{hash_id}";
	# 		pipe->hMSet( hash_key, [
	# 			'campaign_id' => campaign_id,
	# 			'mail_account_addressbook_id' => property_exists(item , 'id') ? item->id : null,
	# 			'mail_account_id' => mail_account.id,
	# 			'spam_base_id' => property_exists(item , 'spam_base_id') ? item->spam_base_id : null,
	# 			'spam_base_record_id' => property_exists(item , 'spam_base_record_id') ? item->spam_base_record_id : null,
	# 			'address' => item->address,
	# 			'name' => item->name,
	# 			'company' => item->company,
	# 			'rest' => item->rest,
	# 			'record_status' => record_status,
	# 			'record_status_txt' => empty(item->record_status_txt) ? record_status_txt : item->record_status_txt,
	# 			'dump_subject' => empty(item->dump_subject) ? '' : item->dump_subject,
	# 			'dump_body' => empty(item->dump_body) ? '' : item->dump_body,
	# 			'dump_headers' => empty(item->dump_headers) ? '' : item->dump_headers,
	# 		]);

	# 		# set expire status to clear data
	# 		pipe->expire(hash_key, expire_time);
	# 		# per account, so pop it in python
	# 		pipe->sAdd(acc_set_key, hash_key);
	# 		# common list
	# 		pipe->rPush(list_key, hash_key);
	# 		# spam bases set
	# 		if (property_exists(item , 'spam_base_id'))
	# 			pipe->sAdd(spambase_key, item->spam_base_id);
	# 	}

	# 	# if( is_null(mail_account.id) || mail_account.id < 1 )
	# 	#  mail_account.id = 'none';
	# 	# store keys for eas of futher usage
	# 	pipe->sAdd(mail_accs_key, acc_set_key);
	# });
