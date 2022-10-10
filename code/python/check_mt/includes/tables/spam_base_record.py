import sqlalchemy, sqlalchemy_utils, datetime
# Database table definitions.
metadata = sqlalchemy.MetaData()
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, SMALLINT, TEXT, MEDIUMTEXT


spam_base_record = sqlalchemy.Table(
    "spam_base_record",
    metadata,
    sqlalchemy.Column('id', INTEGER(unsigned=True), primary_key=True),


    sqlalchemy.Column('address', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('name', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('company', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('rest', sqlalchemy.String(255), nullable=False, server_default='', default=''),

    sqlalchemy.Column('email_account_id', INTEGER(unsigned=True), sqlalchemy.ForeignKey('mail_accounts.id'), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('spam_base_id', INTEGER(unsigned=True), sqlalchemy.ForeignKey('spam_base.id'), nullable=False, server_default='0', default=0),

    sqlalchemy.Column('created_at', sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now(), default=datetime.datetime.utcnow()),
    sqlalchemy.Column('updated_at', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),

    sqlalchemy.Column('mail_account_addressbook_id', INTEGER(unsigned=True), sqlalchemy.ForeignKey('mail_account_addressbook.id'), nullable=False, server_default='0', default=0),


)
