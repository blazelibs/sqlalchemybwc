import sqlalchemy as sa

from plugstack.sqlalchemy import db
from plugstack.sqlalchemy.lib.declarative import declarative_base, DefaultMixin

Base = declarative_base()

colors = sa.Table('colors', db.meta,
    sa.Column('id', sa.Integer, primary_key = True),
    sa.Column('name', sa.String, nullable = False),
)
