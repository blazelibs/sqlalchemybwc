from blazeweb.globals import settings
from blazeweb.hierarchy import visitmods
from paste.registry import StackedObjectProxy
from savalidation import ValidatingSessionExtension
from sqlalchemy import engine_from_config, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session

db = StackedObjectProxy(name="db")

class SQLAlchemyContainer(object):

    def __init__(self):
        self.engine = engine_from_config(dict(settings.db), prefix='')
        self.meta = MetaData()
        self.Session = scoped_session(sessionmaker(bind=self.engine, extension=ValidatingSessionExtension()))

    def get_session(self):
        return self.Session()

class SQLAlchemyApp(object):
    """
        Creates an Sqlalchemy Engine and Metadata for the application

        Sets up thread-local sessions and cleans them up per request
    """
    def __init__(self, application):
        self.application = application
        self.container = SQLAlchemyContainer()
        db._push_object(self.container)
        db.sess = self.container.Session
        visitmods('model.orm')
        visitmods('model.metadata')
        
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
