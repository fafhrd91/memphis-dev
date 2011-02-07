"""

$Id: configlet.py 4711 2011-02-02 22:55:35Z nikolay $
"""
from zope import interface
from memphis import config, controlpanel, ttwschema, storage

from interfaces import _, ITTWProfileConfiglet


class TTWProfileConfiglet(object):
    interface.implements(ITTWProfileConfiglet)

    @property
    def __item__(self):
        try:
            oid = self.__behavior__.getBehaviorOIDs().next()
            item = storage.getItem(oid)
        except StopIteration:
            item = storage.insertItem(self.__behavior__.name)
            item.applyBehavior(ttwschema.ITTWSchema)

        return item

    def __getitem__(self, name):
        schema = ttwschema.ITTWSchema(self.__item__)
        field = schema[name]
        field.__name__ = str(name)
        field.__parent__ = self
        return field


@config.adapter(ITTWProfileConfiglet)
@interface.implementer(ttwschema.ISchema)
def getSchema(configlet):
    return ttwschema.ISchema(configlet.__item__)


config.action(
    controlpanel.registerConfiglet,
    name='principals.profile',
    schema=ITTWProfileConfiglet,
    klass=TTWProfileConfiglet,
    title = _('User profile'),
    description = _('This area allows you to configure user profiles.'))
