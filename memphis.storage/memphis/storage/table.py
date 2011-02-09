import copy, sqlalchemy
from zope import interface, schema
from zope.schema import getFieldsInOrder

from memphis import config
from memphis.storage.hooks import getMetadata
from memphis.storage.interfaces import ISchemaFieldMapper
from memphis.storage.exceptions import StorageException


class FieldMapper(object):
    interface.implements(ISchemaFieldMapper)

    def __init__(self, type):
        self.type = type

    def __call__(self, field):
        return (
            sqlalchemy.Column(
                field.__name__, self.type, 
                default=copy.copy(field.default)),)


config.action(
    config.registerAdapter,
    FieldMapper(sqlalchemy.Unicode), (schema.interfaces.ITextLine,))

config.action(
    config.registerAdapter,
    FieldMapper(sqlalchemy.UnicodeText), (schema.interfaces.IText,))

config.action(
    config.registerAdapter,
    FieldMapper(sqlalchemy.Integer), (schema.interfaces.IInt,))

config.action(
    config.registerAdapter,
    FieldMapper(sqlalchemy.Date), (schema.interfaces.IDate,))

config.action(
    config.registerAdapter,
    FieldMapper(sqlalchemy.DateTime), (schema.interfaces.IDatetime,))

config.action(
    config.registerAdapter,
    FieldMapper(sqlalchemy.Float), (schema.interfaces.IFloat,))

config.action(
    config.registerAdapter,
    FieldMapper(sqlalchemy.Boolean), (schema.interfaces.IBool,))


def getColumns(field):
    columns = ISchemaFieldMapper(field, None)
    if columns is not None:
        return columns

    return (sqlalchemy.Column(field.__name__, sqlalchemy.PickleType),)


def buildTable(name, prefix, schema, columns, reserved=()):
    tbname = name
    for ch in '.-:#':
        tbname = tbname.replace(ch, '_')

    if schema is not None:
        for name, field in getFieldsInOrder(schema):
            if name in reserved:
                raise StorageException(
                    "Field name '%s' is reserved for internal use"%name)
            columns.extend(getColumns(field))

    return sqlalchemy.Table(
        '%s_%s'%(prefix, tbname), getMetadata(), *columns)
