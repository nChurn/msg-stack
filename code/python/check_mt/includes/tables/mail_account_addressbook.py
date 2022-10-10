import sqlalchemy, sqlalchemy_utils, datetime
# Database table definitions.
metadata = sqlalchemy.MetaData()
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, SMALLINT, TEXT, MEDIUMTEXT


mail_account_addressbook = sqlalchemy.Table(
    "mail_account_addressbook",
    metadata,
    sqlalchemy.Column('id', INTEGER(unsigned=True), primary_key=True),
    sqlalchemy.Column('email_account_id', INTEGER(unsigned=True), sqlalchemy.ForeignKey('mail_accounts.id'), nullable=False, server_default='0', default=0),

    sqlalchemy.Column('address', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('name', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('company', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('rest', sqlalchemy.String(255), nullable=False, server_default='', default=''),

    sqlalchemy.Column('send_rule_id', INTEGER(unsigned=True), sqlalchemy.ForeignKey('scan_rules.id'), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('created_at', sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now(), default=datetime.datetime.utcnow()),
    sqlalchemy.Column('updated_at', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),
)
