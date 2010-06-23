from decorator import decorator
from nose.tools import make_decorator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from plugstack.sqlalchemy import db

def is_unique_exc(field_name, exc):
    if not isinstance(exc, IntegrityError):
        return False
    return _is_unique_msg(db.engine.dialect.name, field_name, str(exc))

def _is_unique_msg(dialect, fieldname, msg):
    """
        easier unit testing this way
    """
    if dialect == 'postgresql':
        if 'is not unique' in msg and fieldname in msg:
            return True
    elif dialect == 'mssql':
        if 'unique index' in msg and fieldname in msg:
            return True
        if 'constraint' in msg and fieldname in msg:
            return True
    elif dialect == 'sqlite':
        if 'is not unique' in msg and fieldname in msg:
            return True
    else:
        raise ValueError('is_unique_exc() does not yet support dialect: %s' % dialect)
    return False

def ignore_unique(*fields):
    """
        Wraps the decorated function in a commit/rollback like transwrap() but
        will also ignore unique exceptions for the fields given.
    """
    def decoratorfunc(f):
        def workerfunc(*args, **kwargs):
            should_ignore = kwargs.pop('ignore_unique', None)
            try:
                retval = f(*args, **kwargs)
                db.sess.commit()
                return retval
            except Exception, e:
                db.sess.rollback()
                if not should_ignore:
                    raise
                for field in fields:
                    if is_unique_exc(field, e):
                        return
                raise
        return make_decorator(f)(workerfunc)
    return decoratorfunc

def cm_ignore_unique(*fields):
    """
        like ignore_unique() but makes the decorated function a class method
    """
    def decoratorfunc(f):
        iudf = ignore_unique(*fields)
        workerfunc = iudf(f)
        return classmethod(workerfunc)
    return decoratorfunc

@decorator
def transwrap(f, *args, **kwargs):
    """
        decorates a function so that a DB transaction is always committed after
        the wrapped function returns and also rolls back the transaction if
        an unhandled exception occurs
    """
    try:
        retval = f(*args, **kwargs)
        db.sess.commit()
        return retval
    except Exception:
        db.sess.rollback()
        raise

def cm_transwrap(f):
    """
        like transwrap() but makes the function a class method
    """
    return classmethod(transwrap(f))

@decorator
def one_to_none(f, *args, **kwargs):
    """
        wraps a function that uses SQLAlahcemy's ORM .one() method and returns
        None instead of raising an exception if there was no record returned.
        If multiple records exist, that exception is still raised.
    """
    try:
        return f(*args, **kwargs)
    except NoResultFound, e:
        if 'No row was found for one()' != str(e):
            raise
        return None

def clear_db():
    if db.engine.dialect.name == 'postgresql':
        sql = []
        sql.append('DROP SCHEMA public cascade;')
        sql.append('CREATE SCHEMA public AUTHORIZATION %s;' % db.engine.url.username)
        sql.append('GRANT ALL ON SCHEMA public TO %s;' % db.engine.url.username)
        sql.append('GRANT ALL ON SCHEMA public TO public;')
        sql.append("COMMENT ON SCHEMA public IS 'standard public schema';")
        for exstr in sql:
            try:
                db.engine.execute(exstr)
            except Exception, e:
                print 'WARNING: %s' % e
    elif db.engine.dialect.name == 'sqlite':
        # drop the views
        sql = "select name from sqlite_master where type='view'"
        rows = db.engine.execute(sql)
        for row in rows:
            db.engine.execute('drop view %s' % row['name'])

        # drop the tables
        db.meta.reflect(bind=db.engine)
        for table in reversed(db.meta.sorted_tables):
            try:
                db.engine.execute(table.delete())
            except Exception, e:
                if not 'no such table' in str(e):
                    raise
    elif db.engine.dialect.name == 'mssql':
        mapping = {
            'P': 'drop procedure [%(name)s]',
            'C': 'alter table [%(parent_name)s] drop constraint [%(name)s]',
            ('FN', 'IF', 'TF'): 'drop function [%(name)s]',
            'V': 'drop view [%(name)s]',
            'F': 'alter table [%(parent_name)s] drop constraint [%(name)s]',
            'U': 'drop table [%(name)s]',
        }
        delete_sql = []
        to_repeat_sql = []
        for type, drop_sql in mapping.iteritems():
            sql = 'select name, object_name( parent_object_id ) as parent_name '\
                'from sys.objects where type in (\'%s\')' % '", "'.join(type)
            rows = db.engine.execute(sql)
            for row in rows:
                delete_sql.append(drop_sql % dict(row))
        for sql in delete_sql:
            db.engine.execute(sql)
    else:
        return False
    return True

