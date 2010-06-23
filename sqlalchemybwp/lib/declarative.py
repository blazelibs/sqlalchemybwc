from datetime import datetime
import savalidation as saval
import sqlalchemy as sa
import sqlalchemy.orm as saorm
import sqlalchemy.sql as sasql

class DeclarativeBase(saval.DeclarativeBase):

    id = sa.Column(sa.Integer, primary_key=True)
    createdts = sa.Column(sa.DateTime, nullable=False, server_default=sasql.text('CURRENT_TIMESTAMP'))
    updatedts = sa.Column(sa.DateTime, onupdate=datetime.now)

    def to_dict(self, exclude=[]):
        col_prop_names = [p.key for p in self.__mapper__.iterate_properties \
                                      if isinstance(p, saorm.ColumnProperty)]
        data = dict([(name, getattr(self, name))
                     for name in col_prop_names if name not in exclude])
        return data

def declarative_base(*args, **kwargs):
    kwargs.setdefault('cls', DeclarativeBase)
    return saval.declarative_base(*args, **kwargs)
