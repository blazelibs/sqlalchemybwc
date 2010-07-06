from savalidation import validators as val
import sqlalchemy as sa
import sqlalchemy.sql as sasql

from plugstack.sqlalchemy import db
from plugstack.sqlalchemy.lib.declarative import declarative_base, lookup_base
from plugstack.sqlalchemy.lib.decorators import ignore_unique, transaction

Base = declarative_base(metadata=db.meta)
LookupBase = lookup_base(metadata=db.meta)

class UniqueRecord(Base):
    __tablename__ = 'sabwp_unique_records'

    name = sa.Column(sa.Unicode(255), nullable=False, unique=True)

    @transaction
    def add(cls, name):
        ur = cls()
        ur.name = name
        db.sess.add(ur)
        return ur

    @ignore_unique
    def add_iu(cls, name):
        cls.add(name)

class UniqueRecordTwo(Base):
    __tablename__ = 'sabwp_unique_records_two'

    name = sa.Column(sa.Unicode(255), nullable=False, unique=True)
    email = sa.Column(sa.Unicode(255), nullable=False, unique=True)

    val.validates_constraints()

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

    def __repr__(self):
        return '<Car %s, %s, %s>' % (self.make, self.model, self.year)

class Truck(Base):
    __tablename__ = 'sabwp_trucks'

    make = sa.Column(sa.Unicode(255), nullable=False)
    model = sa.Column(sa.Unicode(255), nullable=False)

    @transaction
    def add(cls, make, model):
        o = cls(make=make, model=model)
        db.sess.add(o)
        return o

    @ignore_unique
    def add_iu(cls, make, model):
        cls.add(make,  model)

sa.Index('uidx_sabwp_truck_makemodel', Truck.make, Truck.model, unique=True)

class CustomerType(LookupBase):
    __tablename__ = 'sabwp_customer_types'
