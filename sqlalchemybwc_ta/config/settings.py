from os import path

from blazeweb.config import DefaultSettings

basedir = path.dirname(path.dirname(__file__))
app_package = path.basename(basedir)


class Default(DefaultSettings):
    def init(self):
        self.dirs.base = basedir
        self.app_package = app_package
        DefaultSettings.init(self)

        self.beaker.enabled = False

        self.add_component(app_package, 'foo')
        self.add_component(app_package, 'sqlalchemy', 'sqlalchemybwc')

        self.add_route('/', 'Index')
        self.add_route('/beaker-test', 'BeakerTest')


class Dev(Default):
    def init(self):
        Default.init(self)
        self.apply_dev_settings()

        self.db.url = 'sqlite://'


class Test(Default):
    def init(self):
        Default.init(self)
        self.apply_test_settings()

        self.db.url = 'sqlite://'

        # uncomment this if you want to use a database you can inspect
        # from os import path
        # self.db.url = 'sqlite:///%s' % path.join(self.dirs.data, 'test_application.db')


class SplitSessionsTest(Default):
    def init(self):
        Default.init(self)
        self.apply_test_settings()

        self.db.url = 'sqlite://'

        self.components.sqlalchemy.use_split_sessions = True


class BeakerSessionTest(Default):
    def init(self):
        Default.init(self)
        self.apply_test_settings()

        self.db.url = 'sqlite:///test_beaker.db'

        self.beaker.enabled = True
        self.beaker.type = 'ext:database'
        self.beaker.cookie_expires = True
        self.beaker.timeout = 60 * 30
        self.beaker.url = self.db.url


try:
    from .site_settings import *  # noqa
except ImportError as e:
    msg = str(e).replace("'", '')
    if 'No module named site_settings' not in msg and \
            'No module named sqlalchemybwc_ta.config.site_settings' not in msg:
        raise

try:
    TestCI  # noqa
except NameError:
    TestCI = Test
