# python package
from zope.location import LocationProxy

from Acquisition import Implicit
from AccessControl import Unauthorized, getSecurityManager

from memphis.content.browser.interfaces import IAddContentForm
from memphis.content.browser.interfaces import IEditContentForm


def CheckPermission(factory):
    def callView(context, request):
        if getSecurityManager().checkPermission(context.permission, context):
            return factory(context, request)

        raise Unauthorized()

    return callView


def CheckTypePermission(factory):
    def callView(context, request):
        if getSecurityManager().checkPermission(
            context.__type__.permission, context):
            return factory(context, request)

        raise Unauthorized()

    return callView


class LocationProxy(LocationProxy, Implicit):
    """ location proxy with acquisition """
