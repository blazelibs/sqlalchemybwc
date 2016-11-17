from .settings import Test


class TestCI(Test):
    """ default profile when running tests """
    def init(self):
        # call parent init to setup default settings
        Test.init(self)
        self.db.url = 'mssql+pymssql://sa:Password12!@localhost:1433/tempdb'
