
from compstack.sqlalchemy import db
from sqlalchemybwc_ta.model.entities import Blog
from sqlalchemybwc_ta.model.schema import colors

class TestBlog(object):

    def setUp(self):
        Blog.delete_all()

    def test_add(self):
        """ this test is just to make sure that middleware.py is auto loading
        model/schema.py.  If it wasn't, then the below would throw an exception. """
        b = Blog.add(title=u'foo')
        assert b.id > 0
        assert b.createdts

class TestColors(object):

    def test_add(self):
        """ this test is just to make sure that middleware.py is auto loading
        model/schema.py.  If it wasn't, then the below would throw an exception. """
        result = db.engine.execute(colors.select())
        assert result
