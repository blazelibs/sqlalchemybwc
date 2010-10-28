"""
    It is expected that most of these decorators will be used on entity class
    methods.  When using them on a regular function, use the decorator with the
    "ncm" postfix:

        ncm => Non-Class Method
"""

from decorator import decorator
from sqlalchemy.orm.exc import NoResultFound

from compstack.sqlalchemy import db
from compstack.sqlalchemy.lib.helpers import is_unique_exc

@decorator
def transaction_ncm(f, *args, **kwargs):
    """
        decorates a function so that a DB transaction is always committed after
        the wrapped function returns and also rolls back the transaction if
        an unhandled exception occurs.

        'ncm' = non class method (version)
    """
    try:
        retval = f(*args, **kwargs)
        db.sess.commit()
        return retval
    except Exception:
        db.sess.rollback()
        raise

def transaction(f):
    """
        like transaction_ncm() but makes the function a class method
    """
    return classmethod(transaction_ncm(f))

@decorator
def ignore_unique_ncm(f, *args, **kwargs):
    """
        Ignores exceptions caused by unique constraints or
        indexes in the wrapped function.

        'ncm' = non class method (version)
    """
    try:
        return f(*args, **kwargs)
    except Exception, e:
        db.sess.rollback()
        if is_unique_exc(e):
                return
        raise

def ignore_unique(f):
    """
        like ignore_unique_ncm() but makes the decorated function a class method
    """
    return classmethod(ignore_unique_ncm(f))

@decorator
def one_to_none_ncm(f, *args, **kwargs):
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

def one_to_none(f):
    """
        like one_to_none_ncm() but makes the decorated function a class method
    """
    return classmethod(one_to_none_ncm(f))
