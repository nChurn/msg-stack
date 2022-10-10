import sqlalchemy, sqlalchemy_utils, datetime
# Database table definitions.
metadata = sqlalchemy.MetaData()
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, SMALLINT, TEXT, MEDIUMTEXT


mail_accounts = sqlalchemy.Table(
    "mail_accounts",
    metadata,
    sqlalchemy.Column('id', INTEGER(unsigned=True), primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('auto_update_name', TINYINT(unsigned=True), nullable=False, server_default='1', default='1'),

    sqlalchemy.Column('smtp_host', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('smtp_port', INTEGER(unsigned=True), nullable=False, server_default='0', default='0'),
    sqlalchemy.Column('smtp_starttls', TINYINT(unsigned=True), nullable=False, server_default='0', default='0'),
    sqlalchemy.Column('smtp_ssl', TINYINT(unsigned=True), nullable=False, server_default='0', default='0'),
    sqlalchemy.Column('smtp_login', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('smtp_password', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('smtp_alive', TINYINT(unsigned=True), nullable=False, server_default='0', default='0'),

    sqlalchemy.Column('pop3_host', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('pop3_port', INTEGER(unsigned=True), nullable=False, server_default='0', default='0'),
    sqlalchemy.Column('pop3_ssl', TINYINT(unsigned=True), nullable=False, server_default='0', default='0'),
    sqlalchemy.Column('pop3_login', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('pop3_password', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('pop3_alive', TINYINT(unsigned=True), nullable=False, server_default='0', default='0'),

    sqlalchemy.Column('imap_host', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('imap_port', INTEGER(unsigned=True), nullable=False, server_default='0', default='0'),
    sqlalchemy.Column('imap_ssl', TINYINT(unsigned=True), nullable=False, server_default='0', default='0'),
    sqlalchemy.Column('imap_login', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('imap_password', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('imap_alive', TINYINT(unsigned=True), nullable=False, server_default='0', default='0'),

    sqlalchemy.Column('enabled', TINYINT(unsigned=True), nullable=False, server_default='0', default='0'),
    sqlalchemy.Column('alive', TINYINT(unsigned=True), nullable=False, server_default='1', default='1'),
    sqlalchemy.Column('test_only', TINYINT(unsigned=True), nullable=False, server_default='0', default='0'),

    sqlalchemy.Column('created_at', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),
    sqlalchemy.Column('updated_at', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),
    sqlalchemy.Column('checked_at', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),
    sqlalchemy.Column('duplicate_insert', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),

    sqlalchemy.Column('check_immediate', TINYINT(unsigned=True), nullable=False, server_default='0', default='0'),
    sqlalchemy.Column('has_errors', TINYINT(unsigned=True), nullable=False, server_default='0', default='0'),
    sqlalchemy.Column('error_log', TEXT(), nullable=False, server_default='', default=''),
    sqlalchemy.Column('error_at', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),

    sqlalchemy.Column('group', sqlalchemy.String(255), nullable=False, server_default='general', default='general'),
    sqlalchemy.Column('need_grab_emails', TINYINT(unsigned=True), nullable=False, server_default='0', default='0'),
    sqlalchemy.Column('intersept', TINYINT(unsigned=True), nullable=False, server_default='0', default='0'),
    sqlalchemy.Column('intersept_updated_at', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),

    sqlalchemy.Column('all_names', TEXT(), nullable=False, server_default='', default=''),

    sqlalchemy.Column('from_mail', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('mail_dumps', INTEGER(unsigned=True), nullable=False, server_default='0', default='0'),
    sqlalchemy.Column('addresses', INTEGER(unsigned=True), nullable=False, server_default='0', default='0'),
    sqlalchemy.Column('web_url', sqlalchemy.String(1024), nullable=False, server_default='', default=''),
    sqlalchemy.Column('web_login', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('web_password', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('web_alive', TINYINT(unsigned=True), nullable=False, server_default='0', default='0'),
)
