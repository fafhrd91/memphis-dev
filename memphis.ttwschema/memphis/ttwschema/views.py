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


class SchemaView(object):

    def update(self):
        sch = self.context

        self.fields = getFieldFactories()
        self.url = self.request.resource_url(self.context)

config.action(
    view.registerPagelet,
    pagelets.ISchemaView, klass = SchemaView,
    template = view.template('memphis.ttwschema:templates/schemaview.pt'))


class AddField(container.AddContentForm):

    @property
    def fields(self):
        return field.Fields(self.context.schema).omit(
            *self.context.ignoreFields)


config.action(
    view.registerView,
    '', IFieldFactory, klass=AddField)


class FieldEdit(form.EditForm):

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


class FieldPreview(form.Form):

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


config.action(
    view.registerView,
    'index.html', IField, klass=FieldEdit)

config.action(
    view.registerView,
    'preview.html', IField, klass=FieldPreview)

config.action(
    view.registerDefaultView,
    'index.html', IField)
