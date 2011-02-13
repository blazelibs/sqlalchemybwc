from blazeweb.globals import settings, rg
from blazeweb.hierarchy import visitmods
from blazeweb.utils import registry_has_object
from paste.registry import StackedObjectProxy
from savalidation import ValidatingSessionExtension
from sqlalchemy import engine_from_config, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session, Session

db = StackedObjectProxy(name="db")

class DebugSession(Session):
    """
        This was helpful in troubleshooting a deadlock condition that
        occured during testing.
    """
    def __init__(self, *args, **kwargs):
        self.dbg_label = kwargs.pop('dbg_label')
        Session.__init__(self, *args, **kwargs)

    def execute(self, clause, params=None, mapper=None, **kw):
        try:
            print 'E>>> ' + self.dbg_label
            return Session.execute(self, clause, params, mapper, **kw)
        finally:
            print '<<<E'

    def _flush(self, objects=None):
        try:
            print '>>>F ' + self.dbg_label
            return Session._flush(self, objects)
        finally:
            print '<<<F'

    def commit(self):
        try:
            print '>>>C ' + self.dbg_label
            return Session.commit(self)
        finally:
            print '<<<C'

class SQLAlchemyContainer(object):

    def __init__(self):
        self.engine = engine_from_config(dict(settings.db), prefix='')
        self.meta = MetaData()
        self.Session = self.make_session()
        if settings.components.sqlalchemy.use_split_sessions:
            self.AppLevelSession = self.make_session()

    def make_session(self, dbg_label = None):
        sm_kwargs = {
            'bind': self.engine,
            'extension': ValidatingSessionExtension(),
        }
        if dbg_label:
            sess_inst = sessionmaker(
                class_ = DebugSession,
                dbg_label = dbg_label,
                **sm_kwargs
            )
        else:
            sess_inst = sessionmaker(**sm_kwargs)
        return scoped_session(sess_inst)

    def get_scoped_session_class(self):
        if settings.components.sqlalchemy.use_split_sessions and not registry_has_object(rg):
            return self.AppLevelSession
        return self.Session

    @property
    def sess(self):
        return self.get_scoped_session_class()

class SQLAlchemyApp(object):
    """
        Creates an Sqlalchemy Engine and Metadata for the application

        Sets up thread-local sessions and cleans them up per request
    """
    def __init__(self, application):
        self.application = application
        self.container = SQLAlchemyContainer()
        db._push_object(self.container)
        visitmods('model.orm')
        visitmods('model.entities')
        visitmods('model.metadata')
        visitmods('model.schema')

    def __call__(self, environ, start_response):
        # clear the session after every response cycle
        def response_cycle_teardown():
            self.container.Session.remove()
        environ.setdefault('blazeweb.response_cycle_teardown', [])
        environ['blazeweb.response_cycle_teardown'].append(response_cycle_teardown)

        # register the db variable for this request/thread
        environ['paste.registry'].register(db, self.container)

        # call the inner application
        return self.application(environ, start_response)
