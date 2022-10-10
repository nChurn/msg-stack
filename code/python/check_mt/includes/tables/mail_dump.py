import sqlalchemy, sqlalchemy_utils, datetime
# Database table definitions.
metadata = sqlalchemy.MetaData()
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, SMALLINT, TEXT, MEDIUMTEXT


mail_dump = sqlalchemy.Table(
    "mail_dump",
    metadata,
    sqlalchemy.Column('id', INTEGER(unsigned=True), primary_key=True),
    # sqlalchemy.Column('mail_account_id', INTEGER(unsigned=True), sqlalchemy.ForeignKey('mail_accounts.id'), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('mail_account_id', INTEGER(unsigned=True), sqlalchemy.ForeignKey('mail_accounts.id'), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('headers', TEXT(), nullable=False, server_default='', default=''),
    sqlalchemy.Column('from', TEXT(), nullable=False, server_default='', default=''),
    sqlalchemy.Column('to', TEXT(), nullable=False, server_default='', default=''),
    sqlalchemy.Column('subject', sqlalchemy.String(1024), nullable=False, server_default='', default=''),
    sqlalchemy.Column('body', MEDIUMTEXT(), nullable=False, server_default='', default=''),
    sqlalchemy.Column('msg_num', sqlalchemy.Integer, nullable=False, server_default='', default=''),
    sqlalchemy.Column('folder_path', sqlalchemy.String(1024), nullable=False, server_default='', default=''),
    sqlalchemy.Column('need_body', TINYINT(unsigned=True), nullable=False, server_default='', default=''),
    sqlalchemy.Column('has_attaches', TINYINT(unsigned=True), nullable=False, server_default='', default=''),
    sqlalchemy.Column('attach_path', TEXT(), nullable=False, server_default='', default=''),
    sqlalchemy.Column('mail_date', sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now(), default=datetime.datetime.utcnow()),
    sqlalchemy.Column('fp_crc', sqlalchemy.String(32), nullable=False, server_default='', default=''),
    sqlalchemy.Column('is_spam', TINYINT(unsigned=True), nullable=False, server_default='', default=''),
)
