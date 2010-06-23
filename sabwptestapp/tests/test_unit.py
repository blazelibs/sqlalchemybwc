from sqlalchemybwp import db
from sqlalchemybwp.lib.decorators import one_to_none
from sqlalchemybwp.lib.helpers import is_unique_exc, _is_unique_msg

from sabwptestapp.model.orm import UniqueRecord, OneToNone, Car, \
    UniqueRecordTwo, Truck

def test_ignore_unique():
    assert UniqueRecord.add(u'test_ignore_unique')

    # unique exception should be ignore with iu version
    assert not UniqueRecord.add_iu(u'test_ignore_unique')

    # transaction should have been rolled back so we can add something else
    # without getting errors
    assert UniqueRecord.add(u'test_ignore_unique_ok')

    # should fail if we don't use the ignore unique (ui) method
    try:
        UniqueRecord.add(u'test_ignore_unique')
        assert False
    except Exception, e:
        if not is_unique_exc(e):
            raise

    # transaction should have been rolled back so we can add something else
    # without getting errors
    assert UniqueRecord.add(u'test_ignore_unique_ok2')

def test_ignore_unique_two():
    assert UniqueRecordTwo.add(u'test_ignore_unique_two', u'tiu@example.com')

    # unique exception should be ignore with iu version
    assert not UniqueRecordTwo.add_iu(u'test_ignore_unique_two', u'tiu@example.com')

    # should fail if we don't use the ignore unique (ui) method
    try:
        UniqueRecordTwo.add(u'test_ignore_unique_two', u'tiu@example.com')
        assert False
    except Exception, e:
        if not is_unique_exc(e):
            raise

def test_ignore_unique_indexes():
    assert Truck.add(u'ford', u'windstar')

    # unique exception should be ignore with iu version
    assert not Truck.add_iu(u'ford', u'windstar')

    # should fail if we don't use the ignore unique (ui) method
    try:
        Truck.add(u'ford', u'windstar')
        assert False
    except Exception, e:
        if not is_unique_exc(e):
            raise

def test_transaction_decorator():
    ur = UniqueRecord.add(u'test_transaction_decorator')
    assert ur.name == u'test_transaction_decorator'
    urid = ur.id
    db.sess.remove()
    ur = UniqueRecord.get(urid)
    assert ur.name == u'test_transaction_decorator'

def test_one_to_none():
    a = OneToNone.add(u'a')
    b1 = OneToNone.add(u'b')
    b2 = OneToNone.add(u'b')

    @one_to_none
    def hasone():
        return db.sess.query(OneToNone).filter_by(ident=u'a').one()

    @one_to_none
    def hasnone():
        return db.sess.query(OneToNone).filter_by(ident=u'c').one()

    @one_to_none
    def hasmany():
        return db.sess.query(OneToNone).filter_by(ident=u'b').one()

    assert a is hasone()
    assert hasnone() is None
    try:
        hasmany()
        assert False, 'expected exception'
    except Exception, e:
        if 'Multiple rows were found for one()' != str(e):
            raise

def test_declarative_stuff():
    c = Car.add(make=u'ford', model=u'windstar', year=u'1998')
    cd = c.to_dict()

    keys = cd.keys()
    assert cd['make'] == u'ford'
    assert cd['model'] == u'windstar'
    assert cd['year'] == 1998
    assert cd['createdts'] is not None
    assert cd['id'] > 0
    assert cd['updatedts'] is None

    c.year = 1999
    db.sess.commit()

    assert c.updatedts is not None

def test_is_unique_msg():
    totest = {
        'sqlite': [
            "(IntegrityError) column name is not unique u'INSERT INTO sabwp_unique_records (name, updatedts) VALUES (?, ?)' (u'test_ignore_unique', None)"
        ],
        'postgresql':[
            """(IntegrityError) duplicate key value violates unique constraint "sabwp_unique_records_name_key" 'INSERT INTO sabwp_unique_records (name, updatedts) VALUES (%(name)s, %(updatedts)s) RETURNING sabwp_unique_records.id' {'updatedts': None, 'name': u'test_ignore_unique'}"""
        ],
        'mssql': [
            """(IntegrityError) ('23000', "[23000] [Microsoft][ODBC SQL Server Driver][SQL Server]Cannot insert duplicate key row in object 'dbo.auth_group' with unique index 'ix_auth_group_name'. (2601) (SQLExecDirectW)")""",
            """(IntegrityError) ('23000', "[23000] [Microsoft][ODBC SQL Server Driver][SQL Server]Violation of UNIQUE KEY constraint 'uc_auth_users_login_id'. Cannot insert duplicate key in object 'dbo.auth_user'. (2627) (SQLExecDirectW)") """
        ]
    }
    def dotest(dialect, msg):
        assert _is_unique_msg(dialect, msg)
    for k,v in totest.iteritems():
        for msg in v:
            yield dotest, k, msg
