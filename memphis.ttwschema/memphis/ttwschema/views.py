"""

$Id: views.py 4730 2011-02-03 05:27:33Z nikolay $
"""
from zope.component import getUtility, queryUtility

from memphis import config, view, container
from memphis.form import field, form, button
from memphis.ttwschema.interfaces import _, ITTWSchema
from memphis.ttwschema.interfaces import IField, IFieldFactory
from memphis.ttwschema.vocabulary import getFieldFactories

import pagelets

config.action(
    view.registerDefaultView,
    'index.html', IField)


class SchemaView(view.Pagelet):
    view.pagelet(
        pagelets.ISchemaView,
        template = view.template('memphis.ttwschema:templates/schemaview.pt'))

    def update(self):
        sch = self.context

        self.fields = getFieldFactories()
        self.url = self.request.resource_url(self.context)


class AddField(container.AddContentForm, view.View):
    view.pyramidView('', IFieldFactory)

    @property
    def fields(self):
        return field.Fields(self.context.schema).omit(
            *self.context.ignoreFields)


class FieldEdit(form.EditForm, view.View):
    view.pyramidView('index.html', IField)

    @property
    def fields(self):
        factory = self.context.__factory__
        return field.Fields(factory.schema).omit(*factory.ignoreFields)

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
        return field.Fields(self.context)

    @property
    def label(self):
        factory = self.context.__factory__
        return u'%s (%s)'%(self.context.__name__, factory.title)

    @property
    def description(self):
        return self.context.__factory__.description

    @button.buttonAndHandler(_('Test field'), name='testfield')
    def handleTestField(self, action):
        data, errors = self.extractData()
        if errors:
            view.addStatusMessage(self.request, self.formErrorsMessage, 'error')
        else:
            view.addStatusMessage(
                self.request, _('Field has been processed successfully.'))


class SchemaPreview(form.Form, view.View):
    view.pyramidView('preview.html', ITTWSchema)

    @property
    def fields(self):
        return field.Fields(self.context.schema)

    @property
    def label(self):
        return self.context.title

    @property
    def description(self):
        return self.context.description

    @button.buttonAndHandler(_('Test schema'), name='testschema')
    def handleTestSchema(self, action):
        data, errors = self.extractData()
        if errors:
            view.addStatusMessage(self.request, self.formErrorsMessage, 'error')
        else:
            view.addStatusMessage(
                self.request, _('Schema has been processed successfully.'))


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


class FieldsAction(container.Action):
    config.adapts(ITTWSchema, 'listing')

    name = 'index.html'
    title = _('Fields')
    description = _('Schema fields')


class SchemaPreviewAction(container.Action):
    config.adapts(ITTWSchema, 'preview')

    name = 'preview.html'
    title = _('Preview')
    description = _('Schema preview')
