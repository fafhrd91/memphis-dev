import sys
from zope import interface
from zope.component import getSiteManager
from memphis import config
from memphis.schema.interfaces import IFieldInformation


class IFieldMarker(interface.Interface):
    """ field marker """


class FieldInformation(object):
    interface.implements(IFieldInformation)

    def __init__(self, name, field, title, description):
        self.name = name
        self.field = field
        self.title = title
        self.description = description

    def getInfo(self, context):
        return self


def getFieldInfos():
    return getSiteManager().adapters.lookupAll(
        (IFieldMarker,), IFieldInformation)


def registerField(name, field, title='', description=''):
    def _registerField(name, field, title, description):
        info = FieldInformation(name, field, title, description)
        config.registerAdapter(info, (IFieldMarker,), IFieldInformation, name)
        config.registerAdapter(
            info.getInfo, (interface.implementedBy(field),), IFieldInformation)

    frame = sys._getframe(1)

    config.action.store.set(
        frame.f_locals, config.action,
        (_registerField, (name, field, title, description),
         {'discriminator': ('memphis.schema:registerField', name)},
         config.getInfo()))

    del frame
