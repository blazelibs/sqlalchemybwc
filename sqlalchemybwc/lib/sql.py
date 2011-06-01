from __future__ import with_statement

from os import path, walk

from blazeweb.hierarchy import findfile, FileNotFound
from compstack.sqlalchemy import db

def run_component_sql(component, target, use_dialect=False):
    ''' see docs for run_app_sql(): usage is the same, execpt for the `component`
        parameter which should be a string representing the name of the
        component.
    '''

    try:
        if _run_dir_sql('%s:sql/%s' % (component, target)):
            return
    except FileNotFound:
        pass

    if use_dialect:
        relative_sql_path = 'sql/%s.%s.sql' % (target, db.engine.dialect.name)
    else:
        relative_sql_path = 'sql/%s.sql' % (target)
    _run_file_sql('%s:%s'%(component,relative_sql_path))

def run_app_sql(target, use_dialect=False):
    ''' used to run SQL from files in an apps "sql" directory:

        For Example:

            run_app_sql('a_directory')

        will run files "<myapp>/sql/a_directory/*.sql

        You can control the dialect used by putting a line like the following at
        the very top of the file:

        -- dialect-require: sqlite

        or

        -- dialect-require: postgresql, mssql

        If the target is not a directory, then:

            run_app_sql('test_setup')

        will run the file "<myapp>/sql/test_setup.sql"

        But, you may also want the dialect taken into account:

            run_app_sql('test_setup', True)

        will run the files:

            # sqlite DB
            /sql/test_setup.sqlite.sql
            # postgres DB
            /sql/test_setup.pgsql.sql
            ...

        The dialect prefix used is the same as the sqlalchemy prefix.

        Any SQL file can contain multiple statements.  They should be seperated
        with the text "--statement-break".

    '''
    try:
        if _run_dir_sql('sql/%s' % target):
            return
    except FileNotFound:
        pass

    if use_dialect:
        relative_sql_path = 'sql/%s.%s.sql' % (target, db.engine.dialect.name )
    else:
        relative_sql_path = 'sql/%s.sql' % target

    _run_file_sql(relative_sql_path)

def _run_dir_sql(rel_path):
    dirpath = findfile(rel_path)
    if not path.isdir(dirpath):
        return False
    for dirname, _, filenames in walk(dirpath):
        filenames.sort()
        for filename in filenames:
            if not filename.endswith('.sql'):
                continue
            with open(path.join(dirname, filename), 'rb') as fh:
                sql_str = fh.read()
            line1, _ = sql_str.split('\n', 1)
            if 'dialect-require:' not in line1 or db.engine.dialect.name in line1:
                _execute_sql_string(sql_str)
    return True

def _run_file_sql(relative_sql_path):
    full_path = findfile(relative_sql_path)
    with open(full_path, 'rb') as fh:
        sql_str = fh.read()
    _execute_sql_string(sql_str)

def _execute_sql_string(sql):
    try:
        for statement in sql.split('--statement-break'):
            statement.strip()
            if statement:
                db.sess.execute(statement)
    except Exception:
        db.sess.rollback()
        raise
