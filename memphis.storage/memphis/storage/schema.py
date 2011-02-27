import sqlalchemy
from zope import interface, schema
from zope.schema import getFieldsInOrder

import hooks
from hooks import getSession
from table import buildTable
from datasheet import DatasheetType
from interfaces import ISchema


class Schema(object):
    interface.implements(ISchema)

    reserved = ('oid',)

    def __init__(self, name, schema, klass, title, description):
        self.name = name
        self.title = title
        self.description = description
        self.spec = schema

        if klass is not None:
            self.Type = klass
        else:
            self.Type = self._buildDatasheetType()

    def apply(self, oid):
        session = getSession()

        ob = session.query(SQLSchema).filter(
            sqlalchemy.and_(
                SQLSchema.oid == oid, SQLSchema.name == self.name)).first()
        if ob is not None:
            return

        session.add(SQLSchema(oid, self.name))
        session.flush()

    def remove(self, oid):
        session = getSession()

        ob = session.query(SQLSchema).filter(SQLSchema.oid == oid).first()
        if ob is None:
            raise KeyError(oid)
        session.delete(ob)

        ob = session.query(self.Type).filter(self.Type.oid == oid).first()
        if ob is not None:
            session.delete(ob)
            hooks.cache.delDatasheet(oid, self.Type)

        session.flush()

    def __call__(self, item):
        return self.getDatasheet(item.oid)

    def getDatasheet(self, oid, create=True):
        klass = self.Type

        ds = hooks.cache.getDatasheet(oid, klass)
        if ds is not None:
            return ds

        session = getSession()
        ds = session.query(klass).filter(klass.oid == oid).first()
        if ds is None:
            if create:
                ds = klass(oid)
                session.add(ds)
                session.flush()
            else:
                return None

        #ds = session.query(klass).filter(klass.oid == oid).first()
        hooks.cache.setDatasheet(oid, klass, ds)

        return ds

    def getSchemaOIDs(self):
        for r in getSession().query(SQLSchema.oid).filter(
            SQLSchema.name == self.name):
            yield r[0]

    def query(self, *args):
        session = getSession()
        if args:
            return session.query(self.Type).filter(*args)
        else:
            return session.query(self.Type)

    def _buildDatasheetType(self):
        columns = [
            sqlalchemy.Column(
                'oid', sqlalchemy.Unicode(32),
                sqlalchemy.ForeignKey('items.oid'), primary_key=True),
        ]

        schema = self.spec

        table = buildTable(self.name, 'schema', schema, columns, self.reserved)

        klass = DatasheetType(
            self.name, schema, title=self.title, description=self.description)
        klass.__table__ = table

        sqlalchemy.orm.mapper(klass, table)
        return klass


class SQLSchema(object):

    def __init__(self, oid, name):
        self.oid = oid
        self.name = name
