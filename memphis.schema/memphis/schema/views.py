from pyramid import url
from webob.exc import HTTPFound
from zope import event
from zope.schema import getFieldsInOrder
from zope.interface import providedBy, implementedBy
from zope.component import \
    getSiteManager, getUtility, queryUtility, getMultiAdapter
from zope.lifecycleevent import ObjectRemovedEvent

from memphis import config, view, container, form
from memphis.schema.interfaces import _
from memphis.schema.interfaces import IField, IFieldFactory
from memphis.schema.interfaces import ISchema, ISchemaManagement
from memphis.schema.interfaces import IWidgetsManagement

import pagelets, ttwschema
from configlet import SchemaFactory


config.action(
    view.registerDefaultView,
    'index.html', IField)

config.action(
    view.registerDefaultView,
    'index.html', ISchema)


config.action(
    view.registerDefaultView,
    'index.html', ISchemaManagement)


class ConfigletView(form.Form, view.View):
    view.pyramidView(
        'index.html', ISchemaManagement,
        template = view.template('memphis.schema:templates/configlet.pt'))

    @form.buttonAndHandler(u'Remove', name='remove')
    def removeHandler(self, action):
        pass


class AddSchema(form.Form, view.View):
    view.pyramidView('', SchemaFactory)

    fields = form.Fields(ISchema).omit('model',)

    label = _('Add schema')

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
            view.addMessage(self.request, self.formErrorsMessage, 'error')
        else:
            view.addMessage(
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
            view.addMessage(self.request, self.formErrorsMessage, 'error')
        else:
            view.addMessage(
                self.request, _('Schema has been processed successfully.'))


class SchemaView(form.Form, view.View):
    view.pyramidView(
        'index.html', ISchema,
        template = view.template('memphis.schema:templates/schemaview.pt'))

    @form.buttonAndHandler(u'Remove', name='remove')
    def removeHandler(self, action):
        ids = self.request.params.getall('field-id')

        for id in ids:
            field = self.context[id]
            event.notify(ObjectRemovedEvent(field, self.context, id))
            del self.context[id]

        if ids:
            view.addMessage(
                self.request, 'Selected fields have been removed.') 

    @form.buttonAndHandler(u'Move up', name='moveup')
    def orderHandler(self, action):
        self.changeOrder(self.request.params.getall('field-id'), 1)

    @form.buttonAndHandler(u'Move down', name='movedown')
    def orderHandler(self, action):
        self.changeOrder(self.request.params.getall('field-id'), -1)

    def changeOrder(self, ids, direction=0):
        context = self.context

        changed = False
        schema = context.schema

        for field_id in ids:
            field = context[field_id]
            fields = [name for name, f in getFieldsInOrder(schema)]

            cur_pos = fields.index(field_id)
            if direction == 1:
                new_pos = cur_pos-1
                if new_pos < 0 or fields[new_pos] in ids:
                    continue

                slice_end = new_pos-1
                if slice_end == -1:
                    slice_end = None
                intervening = [schema[field_id] 
                               for field_id in fields[cur_pos-1:slice_end:-1]]
            else:
                new_pos = cur_pos + 1
                if new_pos > len(ids)+1 or fields[new_pos] in ids:
                    continue
                intervening = [schema[field_id] 
                               for field_id in fields[cur_pos+1:new_pos+1]]

            # changing order
            prev = field.order
            for f in intervening:
                order = f.order
                f.order = prev
                prev = order
            field.order = prev

            changed = True
            context.updateSchema()

        if changed:
            view.addMessage(
                self.request, u'Fields srder has been changed.')


class SchemaEdit(form.EditForm, view.View):
    view.pyramidView('edit.html', ISchema)

    fields = form.Fields(ISchema).omit('model')

    label = 'Modify schema'
    description = 'Modify schema basic attributes.'


class EditAction(container.Action):
    config.adapts(IField, 'edit')

    name = 'index.html'
    title = _('Edit')
    description = _('Field edit form')
    weight = 20


class PreviewAction(container.Action):
    config.adapts(IField, 'preview')

    name = 'preview.html'
    title = _('Preview')
    description = _('Field preview')
    weight = 10


class MoveToSchemaAction(container.Action):
    config.adapts(IField, 'schema')

    name = '../index.html'
    title = _('View schema')
    description = _('Return back to schema.')
    weight = 30


class ViewSchemaAction(container.Action):
    config.adapts(ISchema, 'view')

    name = 'index.html'
    title = _('View')
    description = _('View schema.')
    weight = 10


class FieldsAction(container.Action):
    config.adapts(ISchema, 'listing')

    name = 'edit.html'
    title = _('Edit')
    description = _('Modify ttw schema')
    weight = 20


class SchemaPreviewAction(container.Action):
    config.adapts(ISchema, 'preview')

    name = 'preview.html'
    title = _('Preview')
    description = _('Schema preview')
    weight = 30


class WidgetsManagement(form.Form, view.View):
    view.pyramidView(
        'index.html', IWidgetsManagement,
        template = view.template('memphis.schema:templates/widgets.pt'))

    def update(self):
        super(WidgetsManagement, self).update()

        context = self.context
        self.adapters = getSiteManager().adapters

        fields = []
        for name, factory in self.adapters.lookupAll((ISchema,), IFieldFactory):
            factory = factory(context)
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
