from blazeweb.events import signal
from blazeweb.tasks import run_tasks

def setup_db_structure(sender):
    run_tasks(('clear-db', 'init-db:~test'))
signal('blazeweb.pre_test_init').connect(setup_db_structure)
