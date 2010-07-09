from sqlalchemy.exc import IntegrityError

from plugstack.sqlalchemy import db

def is_unique_exc(exc):
    if not isinstance(exc, IntegrityError):
        return False
    return _is_unique_msg(db.engine.dialect.name, str(exc))

def _is_unique_msg(dialect, msg):
    """
        easier unit testing this way
    """
    if dialect == 'postgresql':
        if 'duplicate key value violates unique constraint' in msg:
            return True
    elif dialect == 'mssql':
        if 'Cannot insert duplicate key' in msg:
            return True
    elif dialect == 'sqlite':
        if 'is not unique' in msg or 'are not unique' in msg:
            return True
    else:
        raise ValueError('is_unique_exc() does not yet support dialect: %s' % dialect)
    return False

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
                table.drop(db.engine)
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
