from blazeweb.hierarchy import findfile
from compstack.sqlalchemy import db

def run_component_sql(component, target, use_dialect=False):
    ''' used to run SQL from files in a component's "sql" directory:

            run_component_sql('mycomponent', 'create_views')

        will run the file "/components/mycomponent/sql/create_views.sql"

            run_component_sql('mycomponent', 'create_views', True)

        will run the files:

            # sqlite DB
            /components/mycomponent/sql/create_views.sqlite.sql
            # postgres DB
            /components/mycomponent/sql/create_views.pgsql.sql
            ...

        The dialect prefix used is the same as the sqlalchemy prefix.

        The SQL file can contain multiple statements.  They should be seperated
        with the text "--statement-break".

    '''
    if use_dialect:
        relative_sql_path = 'sql/%s.%s.sql' % (target, db.engine.dialect.name)
    else:
        relative_sql_path = 'sql/%s.sql' % (target)
    _run_sql('%s:%s'%(component,relative_sql_path))

def run_app_sql(target, use_dialect=False):
    ''' used to run SQL from files in an apps "sql" directory:

            run_app_sql('test_setup')

        will run the file "<myapp>/sql/test_setup.sql"

            run_app_sql('test_setup', True)

        will run the files:

            # sqlite DB
            /sql/test_setup.sqlite.sql
            # postgres DB
            /sql/test_setup.pgsql.sql
            ...

        The dialect prefix used is the same as the sqlalchemy prefix.

        The SQL file can contain multiple statements.  They should be seperated
        with the text "--statement-break".

    '''
    if use_dialect:
        relative_sql_path = 'sql/%s.%s.sql' % (target, db.engine.dialect.name )
    else:
        relative_sql_path = 'sql/%s.sql' % target

    _run_sql(relative_sql_path)

def _run_sql(relative_sql_path):
    full_path = findfile(relative_sql_path)

    sqlfile = file(full_path)
    sql = sqlfile.read()
    sqlfile.close()
    try:
        for statement in sql.split('--statement-break'):
            statement.strip()
            if statement:
                db.sess.execute(statement)
        db.sess.commit()
    except Exception:
        db.sess.rollback()
        raise
