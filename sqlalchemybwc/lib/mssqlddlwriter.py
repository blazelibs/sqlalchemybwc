from os import path
from shutil import rmtree

from blazeweb.utils.filesystem import mkdirs

import sqlalchemy as sa
import sqlalchemy.schema as sasch
import sqlalchemy.sql as sasql
import sqlalchemy.orm as saorm

from compstack.sqlalchemy import db
from compstack.sqlalchemy.lib.declarative import declarative_base, MethodsMixin

Base = declarative_base()

_sysobjs_sql_parent = """
SELECT o.object_id, O.[name], O.type, create_date, modify_date
FROM sys.objects O
where O.type <> ('D', 'PK')
and parent_id = %s
ORDER BY name
"""

_sql_modules_sql = """
SELECT uses_ansi_nulls, uses_quoted_identifier, definition
FROM sys.sql_modules
where object_id = %s
"""

# use a seperate metadata instance because we want the table exactly as it
# appears in the DB and don't want conflicts from db.meta
_ddl_meta = sa.MetaData()

sysobjs = sa.Table('objects', _ddl_meta,
    sa.Column('object_id', sa.Integer, nullable=False),
    sa.Column('parent_object_id', sa.Integer, nullable=False),
    sa.Column('type', sa.String(2), nullable=False),
    sa.Column('name', sa.Unicode(128), nullable=False),
    sa.Column('create_date', sa.DateTime, nullable=False),
    sa.Column('modify_date', sa.DateTime, nullable=False),
    sa.Column('is_ms_shipped', sa.Integer, nullable=False),
    schema='sys'
)

class SysSchema(Base, MethodsMixin):
    __tablename__ = 'schemas'
    __table_args__ = {'schema':'sys'}

    id = sa.Column('schema_id', sa.Integer, nullable=False, primary_key=True)
    name = sa.Column(sa.Unicode(128), nullable=False)

class SysObject(Base, MethodsMixin):
    __tablename__ = 'objects'
    __table_args__ = {'schema':'sys'}

    id = sa.Column('object_id', sa.Integer, nullable=False, primary_key=True)
    parent_object_id = sa.Column(sa.Integer, sa.ForeignKey('sys.objects.object_id'), nullable=False)
    parent = saorm.relation('SysObject', lazy=False, remote_side=[id])
    type = sa.Column(sa.String(2), nullable=False)
    name = sa.Column(sa.Unicode(128), nullable=False)
    create_date = sa.Column(sa.DateTime, nullable=False)
    modify_date = sa.Column(sa.DateTime, nullable=False)
    is_ms_shipped = sa.Column(sa.Integer, nullable=False)
    schema_id = sa.Column(sa.Integer, sa.ForeignKey('sys.schemas.schema_id'), nullable=False)
    schema = saorm.relation(SysSchema, lazy=False)

    def getwriter(self, dump_path):
        type = self.type.strip()
        args = (dump_path, self.id, self.name, self.type, self.create_date, self.modify_date, self)
        if type == 'U':
            return DbTable(*args)
        if type == 'V':
            return DbView(*args)
        if type == 'P':
            return DbStoredProcedure(*args)
        if type in ('FN', 'IF', 'TF'):
            return DbFunction(*args)
        if type == 'TR':
            return DbTrigger(*args)
        if type == 'UQ':
            return DbUniqueConstraint(*args)
        raise ValueError('type "%s" not supported' % type)

class SysColumn(Base, MethodsMixin):
    __tablename__ = 'columns'
    __table_args__ = {'schema':'sys'}

    object_id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=False)
    column_id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=False)
    name = sa.Column(sa.Unicode(128), nullable=False)

class SysFileGroup(Base, MethodsMixin):
    __tablename__ = 'filegroups'
    __table_args__ = {'schema':'sys'}

    name = sa.Column(sa.Unicode(128), nullable=False, primary_key=True)
    data_space_id = sa.Column(sa.Integer, nullable=False)

class SysIndexColumn(Base, MethodsMixin):
    __tablename__ = 'index_columns'
    __table_args__ = {'schema':'sys'}

    object_id = sa.Column(sa.Integer, sa.ForeignKey('sys.indexes.object_id'), sa.ForeignKey('sys.columns.object_id'), nullable=False, primary_key=True, autoincrement=False)
    index_id = sa.Column(sa.Integer, sa.ForeignKey('sys.indexes.index_id'), nullable=False, primary_key=True, autoincrement=False)
    index_column_id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=False)
    column_id = sa.Column(sa.Integer, sa.ForeignKey('sys.columns.column_id'), nullable=False)
    key_ordinal = sa.Column(sa.Integer, nullable=False)
    is_descending_key = sa.Column(sa.Integer, nullable=False)

    column = saorm.relationship(SysColumn, lazy=False, primaryjoin=sasql.and_(
                        SysColumn.object_id == object_id,
                        SysColumn.column_id == column_id
                    )
                )

class SysIndex(Base, MethodsMixin):
    __tablename__ = 'indexes'
    __table_args__ = {'schema':'sys'}

    parent_id = sa.Column('object_id', sa.Integer, sa.ForeignKey('sys.objects.object_id'), nullable=False, primary_key=True, autoincrement=False)
    index_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    name = sa.Column(sa.Unicode(128), nullable=False)
    type_desc = sa.Column(sa.Unicode(60), nullable=False)
    data_space_id = sa.Column(sa.Integer, sa.ForeignKey('sys.filegroups.data_space_id'), nullable=False)

    parent = saorm.relation(SysObject, lazy=False)
    data_space = saorm.relation(SysFileGroup, lazy=False)
    columns = saorm.relation(SysIndexColumn, lazy=False, order_by=SysIndexColumn.key_ordinal,
                    primaryjoin=sasql.and_(
                        SysIndexColumn.object_id == parent_id,
                        SysIndexColumn.index_id == index_id
                    )
                )

class SysForeignKey(Base, MethodsMixin):
    __tablename__ = 'foreign_keys'
    __table_args__ = {'schema':'sys'}

    object_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    parent_object_id = sa.Column(sa.Integer, sa.ForeignKey('sys.objects.object_id'), nullable=False)
    name = sa.Column(sa.Unicode(128), nullable=False)
    delete_referential_action_desc = sa.Column(sa.Unicode(60), nullable=False)
    update_referential_action_desc = sa.Column(sa.Unicode(60), nullable=False)

    def ondelete(self):
        desc = self.delete_referential_action_desc
        if desc == 'NO_ACTION':
            return None
        return desc.replace('_', ' ')

    def onupdate(self):
        desc = self.update_referential_action_desc
        if desc == 'NO_ACTION':
            return None
        return desc.replace('_', ' ')

class DbObject(object):
    def __init__(self, dump_path, oid, name, type, createts, modts, so):
        self.dump_path = dump_path
        self.oid = oid
        self.name = name
        self.type = type.strip()
        self.createts = createts
        self.modts = modts
        self.definition = None
        self.ansi_nulls = None
        self.quoted_ident = None
        self.so = so

        self.type_path = path.join(dump_path, self.folder_name)
        self.file_path = path.join(self.type_path, '%s.sql' % self.name)

        self.populate()

    def populate(self):
        res = db.engine.execute(_sql_modules_sql, [self.oid])
        if not res:
            return
        row = res.fetchone()
        if not row:
            return
        self.definition = row['definition']
        self.ansi_nulls = bool(row['uses_ansi_nulls'])
        self.quoted_ident = bool(row['uses_quoted_identifier'])

    def ddl(self):
        return self.definition or ''

    def file_output(self):
        output = []
        output.append('-- created: %s' % self.createts)
        output.append('-- last updated: %s' % self.modts)
        output.append('')
        if self.ansi_nulls:
            output.append('--statement-break')
            output.append('SET ANSI_NULLS ON')
        if self.quoted_ident:
            output.append('--statement-break')
            output.append('SET QUOTED_IDENTIFIER ON')
        output.append('')
        output.append('--statement-break')
        output.append(self.ddl())
        return '\n'.join(output)

    def write(self):
        with open(self.file_path, 'wb') as fp:
            fp.write( self.file_output() )

class DbTable(DbObject):
    folder_name = 'tables'

    def ddl(self):
        t = sa.Table(self.name, _ddl_meta, autoload=True, autoload_with=db.engine)

        # SA doesn't currently pick up foreign key ON DELETE/UPDATE, so we have
        # to patch those values in
        for c in t.constraints:
            if isinstance(c, sasch.ForeignKeyConstraint):
                sysfk = SysForeignKey.get_by(parent_object_id = self.oid, name=c.name)
                c.ondelete = sysfk.ondelete()
                c.onupdate = sysfk.onupdate()

        table_ddl = str(sasch.CreateTable(t).compile(db.engine))
        uc_ddl = self.uc_ddl()
        return '\n'.join((table_ddl, uc_ddl))

    def write(self):
        DbObject.write(self)
        self.trigger_ddl()

    def uc_ddl(self):
        uc_ddl = []
        res = SysObject.list_where(
            sasql.and_(
                SysObject.parent_object_id == self.oid,
                SysObject.type == u'UQ'
            ),
            order_by=SysObject.name
        )

        for obj in res:
            uc_ddl.append('--statement-break')
            uc_ddl.append(obj.getwriter(self.dump_path).ddl())

        return '\n'.join(uc_ddl)

    def trigger_ddl(self):
        trigger_sql = []
        res = SysObject.list_where(
            sasql.and_(
                SysObject.parent_object_id == self.oid,
                SysObject.type == u'TR'
            ),
            order_by=SysObject.name
        )
        for obj in res:
            twr = obj.getwriter(self.dump_path)
            twr.write()

class DbView(DbObject):
    folder_name = 'views'

class DbStoredProcedure(DbObject):
    folder_name = 'sps'

class DbFunction(DbObject):
    folder_name = 'functions'

class DbTrigger(DbObject):
    folder_name = 'tables'

    def write(self):
        self.file_path = path.join(self.type_path, '%s_trg_%s.sql' % (self.so.parent.name, self.name))
        DbObject.write(self)

class DbUniqueConstraint(DbObject):
    folder_name = ''

    def ddl(self):
        idx = SysIndex.get_by(parent_id=self.so.parent.id, name=self.name)
        ddl = []
        ddl.append('ALTER TABLE')
        ddl.append('[%s].[%s]' % (self.so.parent.schema.name, self.so.parent.name))
        ddl.append('ADD CONSTRAINT [%s] UNIQUE %s' % (self.name, idx.type_desc))
        col_ddl = []
        for c in idx.columns:
            col_ddl.append('[%s] %s' % (c.column.name, 'DESC' if c.is_descending_key else 'ASC'))
        ddl.append('(%s)' % ', '.join(col_ddl))
        ddl.append('ON [%s]' % idx.data_space.name)
        return ' '.join(ddl)

_write_dirs = (
    'tables',
    'views',
    'sps',
    'functions'
)

def writeddl(dump_path):

    if db.engine.dialect.name != 'mssql':
        raise Exception('ERROR: not connected to MSSQL database')

    # delete files that are there and recreate the folders
    for d in _write_dirs:
        target = path.join(dump_path, d)
        if path.isdir(target):
            rmtree(target)
        mkdirs(target)

    # create new files
    res = SysObject.list_where(
        sasql.and_(
            SysObject.type.in_(('U', 'V', 'P', 'FN', 'IF', 'TF')),
            SysObject.is_ms_shipped == 0,
            SysObject.name.in_((u'Users', u'RackInspectionAUDIT'))
        ),
        order_by=SysObject.name
    )
    for obj in res:
        wr = obj.getwriter(dump_path)
        print obj.name
        wr.write()

#def writeddl():
#    db.engine.execute('drop table blog_comments')
#    db.engine.execute('drop table blog')
#    create_sql = """
#    create table blog(
#        id int primary key,
#        title varchar(50)
#    )"""
#
#    db.engine.execute(create_sql)
#
#    create_sql = """create table blog_comments (
#        id int primary key,
#        blog_id int references blog(id) on delete cascade
#    )
#    """
#
#    db.engine.execute(create_sql)
#
#    t = sa.Table('blog_comments', _ddl_meta, autoload=True, autoload_with=db.engine)
#    for c in t.constraints:
#        if isinstance(c, sasch.ForeignKeyConstraint):
#            c.ondelete = 'CASCADE'
#    print str(sasch.CreateTable(t).compile(db.engine))
