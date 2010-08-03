from blazeweb.events import signal
from blazeweb.globals import settings
from blazeweb.tasks import run_tasks

def setup_db_structure(sender):
    if settings.plugins.sqlalchemy.pre_test_init_event_enabled:
        if settings.plugins.sqlalchemy.pre_test_clear_data_only:
            run_tasks('clear-db-data')
        else:
            run_tasks('clear-db')
        run_tasks('init-db:~test')
signal('blazeweb.pre_test_init').connect(setup_db_structure)
