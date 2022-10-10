import sqlalchemy, sqlalchemy_utils, datetime
# Database table definitions.
metadata = sqlalchemy.MetaData()
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, SMALLINT, TEXT, MEDIUMTEXT


attachement_campaign = sqlalchemy.Table(
    "attachement_campaign",
    metadata,
    sqlalchemy.Column('id', INTEGER(unsigned=True), primary_key=True),
    sqlalchemy.Column('campaign_id', INTEGER(unsigned=True), sqlalchemy.ForeignKey('campaign.id'), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('attachement_id', INTEGER(unsigned=True), sqlalchemy.ForeignKey('attachements.id'), nullable=False, server_default='0', default=0),
)
