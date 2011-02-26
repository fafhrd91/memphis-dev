import copy, sqlalchemy
from zope import interface
from memphis import config, storage

from interfaces import IRichText


@config.adapter(IRichText)
@interface.implementer(storage.ISchemaFieldMapper)
def richTextMapper(field):
    return (
        sqlalchemy.Column(
            field.__name__, sqlalchemy.UnicodeText(),
            default=copy.copy(field.default)),
        sqlalchemy.Column(
            '%s_format'%field.__name__, sqlalchemy.Unicode(),
            default=copy.copy(field.default_format)),
        )
