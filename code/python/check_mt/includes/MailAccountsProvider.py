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
from includes.tables.shells import shells
from includes.tables.shell_history import shell_history
from includes.tables.shell_files import shell_files
from includes.tables.scan_rules import scan_rules
from includes.tables.spam_base import spam_base
from includes.tables.spam_base_record import spam_base_record
from includes.tables.bc_socks import bc_socks

from sqlalchemy import or_, and_, func, desc, asc, join
from sqlalchemy.sql.expression import bindparam
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.sql import select, text

from includes.RootLogger import rootLogger
import traceback
import mmh3
import binascii
import concurrent.futures

# TODO: write as normal variant
class MailAccountsProvider():

	#
	def __init__(self, *args, **kwargs):
		self.connection = None

		if 'connection' in kwargs:
			self.connection = kwargs['connection']
		elif '_conn' in kwargs:
			self.connection = kwargs['_conn']
		else:
			self.connection = SQLAlchemyWrapperClass()

		self.prefix = "[MailAccountsProvider] "

	#
	def __exit__(self, type, value, traceback):
		if self.connection is not None:
			self.connection.close()

	def getLatestMailDumpForEmailAccount(self, mail_account_id, _conn=None):
		result = None
		try:
			stmt = select([
						mail_dump.c.id,
						func.max(mail_dump.c.mail_date).label('mail_date'),
						mail_dump.c.fp_crc
					]).\
					select_from(mail_dump).\
					where(mail_dump.c.mail_account_id == mail_account_id).\
					group_by(mail_dump.c.mail_account_id).\
					limit(1)

			# rootLogger.info(f"{self.prefix} getLatestMailDumpForEmailAccount: {stmt}")
			result = self.connection.execute(stmt)
			if result is not None:
				result = result.fetchone()
				# rootLogger.info(f"{self.prefix} getLatestMailDumpForEmailAccount result {result}")
		except Exception as e:
			rootLogger.error(f"{self.prefix}getLatestMailDumpForEmailAccount: {traceback.format_exc()}")
			result = None

		return result

	def getLatestMailDump(self):
		result = None
		try:
			stmt = mail_dump.select().\
					order_by(desc(mail_dump.c.mail_date)).\
					limit(1)

			# rootLogger.info(f"{self.prefix} getLatestMailDump: {stmt}")
			result = self.connection.execute(stmt)
			if result is not None:
				result = result.fetchone()
				# rootLogger.info(f"{self.prefix} getLatestMailDump result {result}")
		except Exception as e:
			rootLogger.error(f"{self.prefix}getLatestMailDump: {traceback.format_exc()}")
			result = None

		return result
