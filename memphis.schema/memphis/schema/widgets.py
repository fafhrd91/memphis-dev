""" Widgets management configlet """
from zope import interface, schema, component
from zope.component import getUtility, getMultiAdapter, queryMultiAdapter
from pyramid.interfaces import IRequest

from memphis import form, config, controlpanel
from memphis.schema.interfaces import IWidgetsManagement, IFieldInformation

import api


class WidgetsManagement(object):
    """ widgets management configlet """
    interface.implements(IWidgetsManagement)

    def updateWidgetMapping(self, data):
        self.data = data


@interface.implementer(form.IDefaultWidget)
@config.adapter(schema.interfaces.IField, IRequest)
def getDefaultWidget(field, request):
    configlet = getUtility(IWidgetsManagement)

    if configlet.data:
        info = IFieldInformation(field, None)
        if info is not None:
            name = configlet.data.get(info.name)
            if name is not None:
                widget = queryMultiAdapter(
                    (field, request), form.IWidget, name=name)
                if widget is not None:
                    return widget

    return getMultiAdapter((field, request), form.IWidget)


config.action(
    controlpanel.registerConfiglet,
    'system.widgets', IWidgetsManagement, WidgetsManagement,
    title = u'Widgets',
    description = u'Widgets management configlet.')
