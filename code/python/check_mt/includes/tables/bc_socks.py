import sqlalchemy, sqlalchemy_utils, datetime
# Database table definitions.
metadata = sqlalchemy.MetaData()
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, SMALLINT, TEXT, MEDIUMTEXT


bc_socks = sqlalchemy.Table(
    "ONLINE",
    metadata,
    sqlalchemy.Column('ID', sqlalchemy.String(128), primary_key=False, nullable=False, server_default='', default=''),
    sqlalchemy.Column('type', TEXT(), nullable=False, server_default='', default=''),
    sqlalchemy.Column('addr', sqlalchemy.String(37), nullable=False, server_default='', default=''),

)
