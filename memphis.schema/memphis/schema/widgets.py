""" Widgets management configlet """
from zope import interface, schema, component
from zope.component import getUtility, getMultiAdapter, queryMultiAdapter
from pyramid.interfaces import IRequest

from memphis import form, config, controlpanel
from memphis.schema.interfaces import IFieldFactory, IWidgetsManagement


class WidgetsManagement(object):
    """ widgets management configlet """
    interface.implements(IWidgetsManagement)

    def updateWidgetMapping(self, data):
        self.data = data

    def getWidgetName(self, field):
        factory = IFieldFactory(field, None)
        if factory is not None:
            if self.data:
                return self.data.get(factory.name)


@interface.implementer(form.IDefaultWidget)
@config.adapter(schema.interfaces.IField, IRequest)
def getDefaultWidget(field, request):
    widget = None
    mng = getUtility(IWidgetsManagement)

    name = mng.getWidgetName(field)
    if name is not None:
        widget = queryMultiAdapter((field, request), form.IWidget, name=name)
        if widget is not None:
            return widget

    return getMultiAdapter((field, request), form.IWidget)


config.action(
    controlpanel.registerConfiglet,
    'system.widgets', IWidgetsManagement, WidgetsManagement,
    title = u'Widgets',
    description = u'Widgets management configlet.')
