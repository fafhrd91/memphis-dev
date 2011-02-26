from pyramid import url
from webob.exc import HTTPFound
from zope import event
from zope.schema import getFieldsInOrder
from zope.interface import providedBy, implementedBy
from zope.component import \
    getSiteManager, getUtility, queryUtility, getMultiAdapter

from memphis import config, view, form
from memphis.schema.interfaces import _, IWidgetsManagement

import api


class WidgetsManagement(form.Form, view.View):
    view.pyramidView(
        'index.html', IWidgetsManagement,
        template = view.template('memphis.schema:templates/widgets.pt'))

    def update(self):
        super(WidgetsManagement, self).update()

        context = self.context
        self.adapters = getSiteManager().adapters

        fields = []
        for name, factory in api.getFieldInfos():
            fields.append(factory)

        fields.sort(key=lambda el: el.title)
        self.fields = fields
        self.requestProvided = providedBy(self.request)

    def getDefault(self, factory):
        if self.context.data:
            return self.context.data.get(factory.name)

    def getWidgets(self, factory):
        widgets = []
        default = None
        for name, widget in self.adapters.lookupAll(
            (implementedBy(factory.field), self.requestProvided), form.IWidget):
            if not name:
                default = widget
            else:
                widgets.append(widget)
        return default, widgets

    @form.buttonAndHandler(u'Save', name='save')
    def saveHandler(self, action):
        data = {}
        for key, val in self.request.params.items():
            if key.startswith('field.'):
                data[key[6:]] = val

        if data:
            self.context.updateWidgetMapping(data)
            view.addMessage(self.request, 'Fields widgets have been saved.')
