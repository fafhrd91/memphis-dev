"""

$Id: schema.py 11783 2011-01-31 00:08:17Z fafhrd91 $
"""
import copy, sqlalchemy
from zope import interface, schema
from zope.schema import getFieldsInOrder

from hooks import getMetadata, getSession
from datasheet import DatasheetType
from interfaces import ISchema
from exceptions import StorageException


class Schema(object):
    interface.implements(ISchema)

    reserved = ('oid',)

    def __init__(self, name, schema, klass, title, description):
        self.name = name
        self.title = title
        self.description = description
        self.specification = schema

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
            raise StorageException('Schema already applied: %s'%self.name)

        session.add(SQLSchema(oid, self.name))
        session.flush()

    def remove(self, oid):
        session = getSession()

        ob = session.query(SQLSchema).filter(SQLSchema.oid == oid).first()
        if ob is None:
            raise KeyError(oid)
        session.delete(ob)

        ob = session.query(self.Type).filter(self.Type.oid == oid).first()
        session.delete(ob)
        session.flush()

    def getDatasheet(self, oid):
        klass = self.Type
        session = getSession()
        ds = session.query(klass).filter(klass.oid == oid).first()
        if ds is None:
            ds = klass(oid)
            session.add(ds)
            session.flush()

        return session.query(klass).filter(klass.oid == oid).first()

    def getSchemaOIDs(self):
        for r in getSession().query(SQLSchema.oid).filter(
            SQLSchema.name == self.name):
            yield r[0]

    def query(self, *args):
        session = getSession()
        return session.query(self.Type).filter(*args)

    @classmethod
    def getItemSchemas(cls, oid):
        return [r[0] for r in getSession().query(
                SQLSchema.name).filter(SQLSchema.oid==oid)]

    def _buildDatasheetType(self):
        columns = [
            sqlalchemy.Column(
                'oid', sqlalchemy.Unicode(32),
                sqlalchemy.ForeignKey('items.oid'), primary_key=True),
        ]

        schema = self.specification

        table = buildTable(self.name, 'schema', schema, columns, self.reserved)

        klass = DatasheetType(
            self.name, schema, title=self.title, description=self.description)

        sqlalchemy.orm.mapper(klass, table)
        return klass


mapping = {
    schema.interfaces.ITextLine: sqlalchemy.Unicode,
    schema.interfaces.IText: sqlalchemy.UnicodeText,
    schema.interfaces.IInt: sqlalchemy.Integer,
    schema.interfaces.IDate: sqlalchemy.Date,
    schema.interfaces.IDatetime: sqlalchemy.DateTime,
    schema.interfaces.IFloat: sqlalchemy.Float,
    schema.interfaces.IBool: sqlalchemy.Boolean,
    }


def buildTable(name, prefix, schema, columns, reserved=()):
    tbname = name
    for ch in '.-:#':
        tbname = tbname.replace(ch, '_')

    if schema is not None:
        for name, field in getFieldsInOrder(schema):
            if name in reserved:
                raise StorageException(
                    "Field name '%s' is reserved for internal use"%name)
            found = False
            for iface, tp in mapping.items():
                if iface.providedBy(field):
                    columns.append(
                        sqlalchemy.Column(
                            name, tp, default=copy.copy(field.default)))
                    found = True
                    break
            if not found:
                columns.append(sqlalchemy.Column(name, sqlalchemy.PickleType))

    return sqlalchemy.Table(
        '%s_%s'%(prefix, tbname), getMetadata(), *columns)


class SQLSchema(object):

    def __init__(self, oid, name):
        self.oid = oid
        self.name = name
