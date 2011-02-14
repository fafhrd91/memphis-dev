import pyramid.url
from webob.exc import HTTPFound
from zope.component import getMultiAdapter

from memphis import form, config, container, view
from memphis.contenttype.interfaces import \
    _, IContentTypeSchema, IContentTypesConfiglet

from memphis.contenttype.configlet import ContentTypeFactory


config.action(
    view.registerDefaultView,
    'index.html', IContentTypesConfiglet)


class ConfigletView(form.Form, view.View):
    view.pyramidView(
        'index.html', IContentTypesConfiglet,
        template = view.template('memphis.contenttype:templates/configlet.pt'))

    @form.buttonAndHandler(u'Remove', name='remove')
    def removeHandler(self, action):
        pass


class AddContentTypeSchema(form.Form, view.View):
    view.pyramidView('', ContentTypeFactory)

    fields = form.Fields(IContentTypeSchema).omit(
        'schemas', 'hiddenFields', 'behaviors', 'behaviorActions', 'widgets')

    label = _('Add content type')

    def createAndAdd(self, data):
        item = self.context.__parent__.create(data)
        self.addedObject = item
        return self.addedObject

    @form.buttonAndHandler(_(u'Add'), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()

        if errors:
            view.addMessage(self.request, self.formErrorsMessage, 'warning')
        else:
            obj = self.createAndAdd(data)

            if obj is not None:
                self.addedObject = obj
                self.finishedAdd = True
                raise HTTPFound(location = '../../')

    @form.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        url = pyramid.url.resource_url(self.context.__parent__, self.request)
        raise HTTPFound(location = url)
