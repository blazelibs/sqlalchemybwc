import sqlalchemy as sa

from compstack.sqlalchemy.lib.declarative import declarative_base, DefaultMixin

Base = declarative_base()

class Blog(Base, DefaultMixin):
    __tablename__ = 'blogs'

    title = sa.Column(sa.Unicode(255), nullable=False)
