from datetime import datetime

from blazeutils.helpers import tolist
import savalidation as saval
import sqlalchemy as sa
from sqlalchemy.ext.declarative import DeclarativeMeta as saDeclarativeMeta
from sqlalchemy.ext.declarative import declarative_base as sa_declarative_base
import sqlalchemy.orm as saorm
import sqlalchemy.sql as sasql

from plugstack.sqlalchemy import db
from plugstack.sqlalchemy.lib.decorators import one_to_none, transaction, \
    ignore_unique

class DeclarativeMeta(saDeclarativeMeta):
    def __init__(cls, classname, bases, dict_):
       cls._add_default_cols()
       return saDeclarativeMeta.__init__(cls, classname, bases, dict_)

    def _add_default_cols(cls):
        cls.id = sa.Column(sa.Integer, primary_key=True)
        cls.createdts = sa.Column(sa.DateTime, nullable=False, server_default=sasql.text('CURRENT_TIMESTAMP'))
        cls.updatedts = sa.Column(sa.DateTime, onupdate=datetime.now)

class DeclarativeBase(saval.DeclarativeBase):

    @transaction
    def add(cls, **kwargs):
        o = cls()
        o.from_dict(kwargs)
        db.sess.add(o)
        return o

    @ignore_unique
    def add_iu(cls, **kwargs):
        """
            Add a record and ignore unique constrainted related
            exceptions if encountered
        """
        return cls.add(**kwargs)

    @transaction
    def edit(cls, oid=None, **kwargs):
        try:
            oid = oid or kwargs.pop('id')
        except KeyError:
            raise ValueError('the id must be given to edit the record')
        o = cls.get(oid)
        o.from_dict(kwargs)
        return o

    @classmethod
    def update(cls, oid=None, **kwargs):
        """
            Add or edit depending on presence if 'id' field from oid or kwargs
        """
        oid = oid or kwargs.pop('id', None)
        if oid:
            return cls.edit(oid, **kwargs)
        return cls.add(**kwargs)

    @classmethod
    def get(cls, oid):
        return db.sess.query(cls).get(oid)

    @one_to_none
    def get_by(cls, **kwargs):
        """
        Returns the instance of this class matching the given criteria or None
        if there is no record matching the criteria.

        If multiple records are returned, an exception is raised.
        """
        return db.sess.query(cls).filter_by(**kwargs).one()

    @one_to_none
    def get_where(cls, clause, *extra_clauses):
        """
        Returns the instance of this class matching the given clause(s) or None
        if there is no record matching the criteria.

        If multiple records are returned, an exception is raised.
        """
        where_clause = cls.combine_clauses(clause, extra_clauses)
        return db.sess.query(cls).filter(where_clause).one()

    @classmethod
    def first(cls, order_by=None):
        return cls.order_by_helper(db.sess.query(cls), order_by).first()

    @classmethod
    def first_by(cls, order_by=None, **kwargs):
        return cls.order_by_helper(db.sess.query(cls), order_by).filter_by(**kwargs).first()

    @classmethod
    def first_where(cls, clause, *extra_clauses, **kwargs):
        order_by = kwargs.pop('order_by', None)
        if kwargs:
            raise ValueError('order_by is the only acceptable keyword arg')
        where_clause = cls.combine_clauses(clause, extra_clauses)
        return cls.order_by_helper(db.sess.query(cls), order_by).filter(where_clause).first()

    @classmethod
    def list(cls, order_by=None):
        return cls.order_by_helper(db.sess.query(cls), order_by).all()

    @classmethod
    def list_by(cls, order_by=None, **kwargs):
        return cls.order_by_helper(db.sess.query(cls), order_by).filter_by(**kwargs).all()

    @classmethod
    def list_where(cls, clause, *extra_clauses, **kwargs):
        order_by = kwargs.pop('order_by', None)
        if kwargs:
            raise ValueError('order_by is the only acceptable keyword arg')
        where_clause = cls.combine_clauses(clause, extra_clauses)
        return cls.order_by_helper(db.sess.query(cls), order_by).filter(where_clause).all()

    @classmethod
    def pairs(cls, fields, order_by=None, _result=None):
        """
            Returns a list of two element tuples.
            [
                (1, 'apple')
                (2, 'banana')
            ]

            fields: string with the name of the fields you want to pair with
                a ":" seperating them.  I.e.:

                Fruit.pairs('id:name')

            order_by = order_by clause or iterable of order_by clauses
        """
        key_field_name, value_field_name = fields.split(':')
        if not _result:
            _result = cls.list(order_by)
        retval = []
        for obj in _result:
            retval.append((
                  getattr(obj, key_field_name),
                  getattr(obj, value_field_name)
                ))
        return retval

    @classmethod
    def pairs_by(cls, fields, order_by=None, **kwargs):
        result = cls.list_by(order_by, **kwargs)
        return cls.pairs(fields, _result=result)

    @classmethod
    def pairs_where(cls, fields, clause, *extra_clauses, **kwargs):
        result = cls.list_where(clause, *extra_clauses, **kwargs)
        return cls.pairs(fields, _result=result)

    @transaction
    def delete(cls, oid):
        o = cls.get(oid)
        if o is None:
            return False

        db.sess.delete(o)
        return True

    @transaction
    def delete_where(cls, clause, *extra_clauses):
        where_clause = cls.combine_clauses(clause, extra_clauses)
        result = db.sess.execute(cls.__table__.delete().where(where_clause))
        return result.rowcount

    @transaction
    def delete_all(cls):
        result = db.sess.execute(cls.__table__.delete())
        return result.rowcount

    @classmethod
    def count(cls):
        return db.sess.query(cls).count()

    @classmethod
    def count_by(cls, **kwargs):
        return db.sess.query(cls).filter_by(**kwargs).count()

    @classmethod
    def count_where(cls, clause, *extra_clauses):
        where_clause = cls.combine_clauses(clause, extra_clauses)
        return db.sess.query(cls).filter(where_clause).count()

    def to_dict(self, exclude=[]):
        col_prop_names = [p.key for p in self.__mapper__.iterate_properties \
                                      if isinstance(p, saorm.ColumnProperty)]
        data = dict([(name, getattr(self, name))
                     for name in col_prop_names if name not in exclude])
        return data

    def from_dict(self, data):
        """
        Update a mapped class with data from a JSON-style nested dict/list
        structure.
        """
        # surrogate can be guessed from autoincrement/sequence but I guess
        # that's not 100% reliable, so we'll need an override

        mapper = saorm.object_mapper(self)

        for key, value in data.iteritems():
            if isinstance(value, dict):
                dbvalue = getattr(self, key)
                rel_class = mapper.get_property(key).mapper.class_
                pk_props = rel_class._descriptor.primary_key_properties

                # If the data doesn't contain any pk, and the relationship
                # already has a value, update that record.
                if not [1 for p in pk_props if p.key in data] and \
                   dbvalue is not None:
                    dbvalue.from_dict(value)
                else:
                    record = rel_class.update_or_create(value)
                    setattr(self, key, record)
            elif isinstance(value, list) and \
                 value and isinstance(value[0], dict):

                rel_class = mapper.get_property(key).mapper.class_
                new_attr_value = []
                for row in value:
                    if not isinstance(row, dict):
                        raise Exception(
                                'Cannot send mixed (dict/non dict) data '
                                'to list relationships in from_dict data.')
                    record = rel_class.update_or_create(row)
                    new_attr_value.append(record)
                setattr(self, key, new_attr_value)
            else:
                setattr(self, key, value)

    @classmethod
    def order_by_helper(cls, query, order_by):
        if order_by is not None:
            return query.order_by(*tolist(order_by))
        return query.order_by(cls.id)

    @classmethod
    def combine_clauses(cls, clause, extra_clauses):
        if not extra_clauses:
            return clause
        return sasql.and_(clause, *extra_clauses)

def declarative_base(*args, **kwargs):
    kwargs.setdefault('cls', DeclarativeBase)
    kwargs.setdefault('metaclass', DeclarativeMeta)
    return sa_declarative_base(*args, **kwargs)
