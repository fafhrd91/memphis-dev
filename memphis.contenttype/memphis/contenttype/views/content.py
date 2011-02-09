import pyramid.url
from webob.exc import HTTPFound

from zope import interface
from zope.component import getUtility, queryUtility
from memphis import form, config, container, view, storage, ttwschema

from memphis.contenttype.interfaces import _, IContent, IContentType


class AddContent(form.EditForm, container.AddContentForm, view.View):
    view.pyramidView('', IContentType)

    fields = form.Fields()
    validate = container.AddContentForm.validate

    @property
    def label(self):
        return 'Add content: %s'%self.context.title

    @property
    def description(self):
        return self.context.description

    def listWrappedForms(self):
        ct = IContentType(self.context)

        forms = []
        datasheets = {}
        for schId in tuple(self.context.schemas):
            schema = queryUtility(storage.ISchema, schId)
            if schema is not None:
                ds = schema.Type()
                datasheets[schema.name] = ds
                form = EditDatasheet(ds, self.request, self)
                form.update()
                forms.append((schId, form))

        self.datasheets = datasheets
        return forms

    @form.buttonAndHandler(_(u'Add'), name='apply')
    def handleAdd(self, action):
        data, errors = self.extractData()

        if errors:
            view.addStatusMessage(
                self.request, (self.formErrorsMessage,) + errors, 'formError')
            return

        changes = self.applyChanges(data)

        obj = self.createAndAdd(data)
        if obj is not None:
            self.addedObject = obj
            self.finishedAdd = True
            raise HTTPFound(location = self.nextURL())


class EditDatasheet(form.SubForm):

    @property
    def prefix(self):
        return self.context.__id__

    @property
    def fields(self):
        iface = self.context.__schema__
        if iface.isOrExtends(IContent):
            return form.Fields(self.context.__schema__).omit('type')
        else:
            return form.Fields(self.context.__schema__)

    @property
    def label(self):
        return self.context.__title__

    @property
    def description(self):
        return self.context.__description__


class EditContent(form.EditForm, view.View):
    view.pyramidView('edit.html', IContent)

    fields = form.Fields()

    label = 'Modify content'

    def listWrappedForms(self):
        ct = IContentType(self.context)

        forms = []
        for schId in ct.schemas:
            schema = queryUtility(storage.ISchema, schId)
            if schema is not None:
                ds = self.context.getDatasheet(schema.specification)
                form = EditDatasheet(ds, self.request, self)
                form.update()
                forms.append((schId, form))

        return forms
