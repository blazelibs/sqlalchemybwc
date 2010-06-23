import sqlalchemy as sa
import sqlalchemy.sql as sasql

from plugstack.sqlalchemy import db
from plugstack.sqlalchemy.lib.declarative import declarative_base
from plugstack.sqlalchemy.lib.helpers import cm_ignore_unique, cm_transwrap

Base = declarative_base(metadata=db.meta)

class UniqueRecord(Base):
    __tablename__ = 'sabwp_unique_records'

    name = sa.Column(sa.Unicode(255), nullable=False, unique=True)

    @cm_ignore_unique('name')
    def add(cls, name, inactive_flag = False):
        ur = cls()
        ur.name = name
        db.sess.add(ur)
        return ur

    @cm_ignore_unique('foobar')
    def add2(cls, name, inactive_flag = False):
        ur = cls()
        ur.name = name
        db.sess.add(ur)
        return ur

    @cm_ignore_unique('foobar', 'name')
    def add3(cls, name, inactive_flag = False):
        ur = cls()
        ur.name = name
        db.sess.add(ur)
        return ur

    @classmethod
    def get(cls, recid):
        return db.sess.query(cls).get(recid)

class OneToNone(Base):
    __tablename__ = 'sabwp_onetonone_records'

    ident = sa.Column(sa.Unicode(255), nullable=False)

    @cm_transwrap
    def add(cls, ident):
        o = cls()
        o.ident = ident
        db.sess.add(o)
        return o

class Car(Base):
    __tablename__ = 'sabwp_cars'

    make = sa.Column(sa.Unicode(255), nullable=False)
    model = sa.Column(sa.Unicode(255), nullable=False)
    year = sa.Column(sa.Integer, nullable=False)

    @cm_transwrap
    def add(cls, **kwargs):
        o = cls(**kwargs)
        db.sess.add(o)
        return o
