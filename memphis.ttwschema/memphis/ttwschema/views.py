"""

$Id: views.py 4730 2011-02-03 05:27:33Z nikolay $
"""
from pyramid import url
from webob.exc import HTTPFound
from zope import event
from zope.component import getUtility, queryUtility, getMultiAdapter
from zope.lifecycleevent import ObjectRemovedEvent

from memphis import config, view, container, form
from memphis.ttwschema.interfaces import _
from memphis.ttwschema.interfaces import IField, IFieldFactory
from memphis.ttwschema.interfaces import ISchema, ISchemaManagement

import pagelets
from configlet import SchemaFactory


config.action(
    view.registerDefaultView,
    'index.html', IField)

config.action(
    view.registerDefaultView,
    'index.html', ISchema)


class Listing(view.View):
    view.pyramidView(
        'index.html', ISchemaManagement,
        template = view.template('memphis.ttwschema:templates/management.pt'))


class AddSchema(form.Form, view.View):
    view.pyramidView('', SchemaFactory)

    fields = form.Fields(ISchema).omit('model', 'published', 'publishedmodel')

    label = _('Add schema')

    def createAndAdd(self, data):
        item = self.context.__parent__.create(data)
        self.addedObject = item
        return self.addedObject

    @form.buttonAndHandler(_(u'Add'), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()

        if errors:
            view.addStatusMessage(
                self.request, self.formErrorsMessage, 'warning')
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


class FieldEdit(form.EditForm, view.View):
    view.pyramidView('index.html', IField)

    @property
    def fields(self):
        factory = self.context.__factory__
        return form.Fields(factory.schema).omit(*factory.hiddenFields)

    @property
    def label(self):
        return self.context.__factory__.title

    @property
    def description(self):
        return self.context.__factory__.description


class FieldPreview(form.Form, view.View):
    view.pyramidView('preview.html', IField)

    @property
    def fields(self):
        return form.Fields(self.context)

    @property
    def label(self):
        factory = self.context.__factory__
        return u'%s (%s)'%(self.context.__name__, factory.title)

    @property
    def description(self):
        return self.context.__factory__.description

    @form.buttonAndHandler(_('Test field'), name='testfield')
    def handleTestField(self, action):
        data, errors = self.extractData()
        if errors:
            view.addStatusMessage(self.request, self.formErrorsMessage, 'error')
        else:
            view.addStatusMessage(
                self.request, _('Field has been processed successfully.'))


class SchemaPreview(form.Form, view.View):
    view.pyramidView('preview.html', ISchema)

    @property
    def fields(self):
        return form.Fields(self.context.schema)

    @property
    def label(self):
        return self.context.title

    @property
    def description(self):
        return self.context.description

    @form.buttonAndHandler(_('Test schema'), name='testschema')
    def handleTestSchema(self, action):
        data, errors = self.extractData()
        if errors:
            view.addStatusMessage(self.request, self.formErrorsMessage, 'error')
        else:
            view.addStatusMessage(
                self.request, _('Schema has been processed successfully.'))


class SchemaView(view.View):
    view.pyramidView(
        'index.html', ISchema,
        template = view.template('memphis.ttwschema:templates/schemaview.pt'))

    def update(self):
        request = self.request
        self.url = url.resource_url(self.context, request)

        if 'form.remove' in request.params:
            ids = request.params.getall('field-id')

            context = self.context
            for id in ids:
                field = context[id]
                event.notify(ObjectRemovedEvent(field, context, id))
                del context[id]

            if ids:
                view.addStatusMessage(
                    request, 'Selected fields have been removed.') 


class SchemaEdit(form.EditForm, view.View):
    view.pyramidView('edit.html', ISchema)

    fields = form.Fields(ISchema).omit('model')

    label = 'Modify schema'


class EditAction(container.Action):
    config.adapts(IField, 'edit')

    name = 'index.html'
    title = _('Edit')
    description = _('Field edit form')


class PreviewAction(container.Action):
    config.adapts(IField, 'preview')

    name = 'preview.html'
    title = _('Preview')
    description = _('Field preview')


class ViewSchemaAction(container.Action):
    config.adapts(ISchema, 'view')

    name = 'index.html'
    title = _('View schema')
    description = _('View schema.')


class FieldsAction(container.Action):
    config.adapts(ISchema, 'listing')

    name = 'edit.html'
    title = _('Edit schema')
    description = _('Schema fields')


class SchemaPreviewAction(container.Action):
    config.adapts(ISchema, 'preview')

    name = 'preview.html'
    title = _('Preview')
    description = _('Schema preview')
