import sqlalchemy, sqlalchemy_utils, datetime
# Database table definitions.
metadata = sqlalchemy.MetaData()
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, SMALLINT, TEXT, MEDIUMTEXT


attachements = sqlalchemy.Table(
    "attachements",
    metadata,
    sqlalchemy.Column('id', INTEGER(unsigned=True), primary_key=True),
    sqlalchemy.Column('campaign_id', INTEGER(unsigned=True), sqlalchemy.ForeignKey('campaign.id'), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('name', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('size', INTEGER(unsigned=True), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('path', sqlalchemy.String(255), nullable=False, server_default='None', default='None'),
    sqlalchemy.Column('data', sqlalchemy.LargeBinary(), nullable=True),
    sqlalchemy.Column('group', sqlalchemy.String(255), nullable=False, server_default='None', default='None'),
    sqlalchemy.Column('used', INTEGER(unsigned=True), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('created_at', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),
    sqlalchemy.Column('updated_at', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),
)
