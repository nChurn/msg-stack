import sqlalchemy, sqlalchemy_utils, datetime
# Database table definitions.
metadata = sqlalchemy.MetaData()
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, SMALLINT, TEXT, MEDIUMTEXT


spam_base = sqlalchemy.Table(
    "spam_base",
    metadata,
    sqlalchemy.Column('id', INTEGER(unsigned=True), primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('filters', sqlalchemy.String(255), nullable=False, server_default='', default=''),

    sqlalchemy.Column('created_at', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),
    sqlalchemy.Column('updated_at', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),

    sqlalchemy.Column('enable_automatics', TINYINT(unsigned=True), nullable=False, server_default='0', default='0'),

)
