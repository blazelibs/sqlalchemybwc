from sqlalchemybwp import db
from sqlalchemybwp.lib.helpers import is_unique_exc, one_to_none

from sabwptestapp.model.orm import UniqueRecord, OneToNone, Car

def test_ignore_unique():
    assert UniqueRecord.add(u'test_ignore_unique')
    assert not UniqueRecord.add(u'test_ignore_unique', ignore_unique=True)

    # should fail if we don't send ignore_unique
    try:
        UniqueRecord.add2(u'test_ignore_unique')
        assert False
    except Exception, e:
        if not is_unique_exc('name', e):
            raise

def test_ignoring_different_field():
    assert UniqueRecord.add2(u'test_ignoring_different_field')

    try:
        UniqueRecord.add2(u'test_ignoring_different_field', ignore_unique=True)
        assert False
    except Exception, e:
        if not is_unique_exc('name', e):
            raise

def test_ignoring_multi_fields():
    assert UniqueRecord.add2(u'test_ignoring_multi_fields')
    assert not UniqueRecord.add(u'test_ignoring_multi_fields', ignore_unique=True)

def test_transwrapcm():
    ur = UniqueRecord.add(u'test_transwrapcm')
    assert ur.name == u'test_transwrapcm'
    urid = ur.id
    db.sess.remove()
    ur = UniqueRecord.get(urid)
    assert ur.name == u'test_transwrapcm'

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
