import sqlalchemy, sqlalchemy_utils, datetime
# Database table definitions.
metadata = sqlalchemy.MetaData()
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, SMALLINT, TEXT, MEDIUMTEXT


scan_rules = sqlalchemy.Table(
    "scan_rules",
    metadata,
    sqlalchemy.Column('id', INTEGER(unsigned=True), primary_key=True),
    sqlalchemy.Column('rule', sqlalchemy.String(255), nullable=False, server_default='', default=''),
    sqlalchemy.Column('group', sqlalchemy.String(255), nullable=False, server_default='', default=''),

    sqlalchemy.Column('exclude', TINYINT(unsigned=True), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('enabled', TINYINT(unsigned=True), nullable=False, server_default='0', default=0),
    sqlalchemy.Column('created_at', sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now(), default=datetime.datetime.utcnow()),
    sqlalchemy.Column('updated_at', sqlalchemy.DateTime, nullable=True, server_default=None, default=None),
)
