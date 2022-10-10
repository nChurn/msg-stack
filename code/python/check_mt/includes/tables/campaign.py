import sqlalchemy, sqlalchemy_utils, datetime
# Database table definitions.
metadata = sqlalchemy.MetaData()
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, SMALLINT, TEXT, MEDIUMTEXT


campaign = sqlalchemy.Table(
    "campaign",
    metadata,
    sqlalchemy.Column('id', INTEGER(unsigned=True), primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('subject', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('body', TEXT(), nullable=False, server_default='', default=''),

    sqlalchemy.Column('is_html', TINYINT(unsigned=True), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('headers', TEXT(), nullable=False, server_default='', default=''),
    sqlalchemy.Column('account_name', sqlalchemy.String(255), nullable=False, server_default='None', default='None'),

    sqlalchemy.Column('max_messages', INTEGER(unsigned=True), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('per_time', INTEGER(unsigned=True), nullable=False, server_default='0', default=0),

    sqlalchemy.Column('ignore_selfhost', TINYINT(unsigned=True), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('reply_mode', TINYINT(unsigned=True), nullable=False, server_default='0', default=0),

    sqlalchemy.Column('reply_days', INTEGER(unsigned=True), nullable=False, server_default='90', default=90),
    sqlalchemy.Column('status', INTEGER(unsigned=True), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('workers', INTEGER(unsigned=True), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('total_emails', INTEGER(unsigned=True), nullable=False, server_default='0', default=0),

    sqlalchemy.Column('created_at', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),
    sqlalchemy.Column('updated_at', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),

    sqlalchemy.Column('scheduled_to', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),
    sqlalchemy.Column('scheduled', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),

    sqlalchemy.Column('started_at', sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now(), default=datetime.datetime.utcnow()),
    sqlalchemy.Column('finnished_at', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),

    sqlalchemy.Column('filters', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('attach_name', sqlalchemy.String(255), nullable=False, server_default='', default=''),

    sqlalchemy.Column('ignore_accounts', INTEGER(unsigned=True), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('fail_behaviour', INTEGER(unsigned=True), nullable=False, server_default='0', default=0),

    sqlalchemy.Column('check_send', INTEGER(unsigned=True), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('has_attaches', TINYINT(unsigned=True), nullable=False, server_default='1', default=1),
)
