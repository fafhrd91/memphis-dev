""" various utils """
import sys
from zope import interface
from zope.security.permission import Permission
from zope.security.interfaces import IPermission
from AccessControl.Permission import addPermission
from plone.app.content.interfaces import INameFromTitle

from memphis import config
from memphis.content.interfaces import IContentSchema


def registerPermission(id, title, roles=()):
    def _registerPermission():
        permission = Permission(id, title, '')
        config.registerUtility(permission, IPermission, id)

        z2_permission = str(title)
        if roles:
            addPermission(z2_permission, default_roles=tuple(roles))
        else:
            addPermission(z2_permission)

    config.action(_registerPermission, __frame=sys._getframe(1))


class NameFromTitle(object):
    interface.implements(INameFromTitle)
    config.adapts(IContentSchema)

    def __init__(self, ob):
        self.title = IContentSchema(ob).title
