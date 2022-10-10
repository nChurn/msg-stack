import sqlalchemy, sqlalchemy_utils, datetime
# Database table definitions.
metadata = sqlalchemy.MetaData()
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, SMALLINT, TEXT, MEDIUMTEXT


campaign_mail_accounts = sqlalchemy.Table(
    "campaign_mail_accounts",
    metadata,
    sqlalchemy.Column('id', INTEGER(unsigned=True), primary_key=True),
    sqlalchemy.Column('campaign_id', INTEGER(unsigned=True), sqlalchemy.ForeignKey('campaign.id'), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('mail_account_id', INTEGER(unsigned=True), sqlalchemy.ForeignKey('mail_accounts.id'), nullable=False, server_default='0', default=0),
)
