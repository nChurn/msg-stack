import sqlalchemy, sqlalchemy_utils, datetime
# Database table definitions.
metadata = sqlalchemy.MetaData()
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, SMALLINT, TEXT, MEDIUMTEXT


mail_account_addresbook_maildump = sqlalchemy.Table(
    "mail_account_addresbook_maildump",
    metadata,
    sqlalchemy.Column('id', INTEGER(unsigned=True), primary_key=True),
    sqlalchemy.Column('addressbook_id', INTEGER(unsigned=True), sqlalchemy.ForeignKey('mail_account_addressbook.id'), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('mail_account_id', INTEGER(unsigned=True), sqlalchemy.ForeignKey('mail_accounts.id'), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('mail_dump_id', INTEGER(unsigned=True), sqlalchemy.ForeignKey('mail_dump.id'), nullable=False, server_default='0', default=0),
)
