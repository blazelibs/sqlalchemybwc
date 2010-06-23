import sqlalchemy as sa
import sqlalchemy.sql as sasql

from plugstack.sqlalchemy import db
from plugstack.sqlalchemy.lib.declarative import declarative_base
from plugstack.sqlalchemy.lib.decorators import ignore_unique, transaction

Base = declarative_base(metadata=db.meta)

class UniqueRecord(Base):
    __tablename__ = 'sabwp_unique_records'

    name = sa.Column(sa.Unicode(255), nullable=False, unique=True)

    @transaction
    def add(cls, name, inactive_flag = False):
        ur = cls()
        ur.name = name
        db.sess.add(ur)
        return ur

    @ignore_unique
    def add_iu(cls, name, inactive_flag = False):
        cls.add(name, inactive_flag)

    @classmethod
    def get(cls, oid):
        return db.sess.query(cls).get(oid)

class OneToNone(Base):
    __tablename__ = 'sabwp_onetonone_records'

    ident = sa.Column(sa.Unicode(255), nullable=False)

    @transaction
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

    @transaction
    def add(cls, **kwargs):
        o = cls(**kwargs)
        db.sess.add(o)
        return o
