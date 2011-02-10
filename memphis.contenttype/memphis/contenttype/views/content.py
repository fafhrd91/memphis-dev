import pyramid.url
from webob.exc import HTTPFound

from zope import interface
from zope.component import getUtility, queryUtility
from memphis import form, config, container, view, storage, ttwschema

from memphis.contenttype import schemas
from memphis.contenttype.interfaces import _, IContent, IContentType


config.action(
    view.registerDefaultView,
    'index.html', IContent)


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
                if schId in ct.hiddenFields:
                    form.hidden = ct.hiddenFields[schId]
                form.update()
                forms.append((schId, form))

        self.datasheets = datasheets
        return forms

    @form.buttonAndHandler(_(u'Add'), name='apply')
    def handleAdd(self, action):
        data, errors = self.extractData()

        if errors:
            view.addMessage(
                self.request, (self.formErrorsMessage,) + errors, 'formError')
            return

        changes = self.applyChanges(data)

        obj = self.createAndAdd(self.datasheets)
        if obj is not None:
            self.addedObject = obj
            self.finishedAdd = True
            raise HTTPFound(location = self.nextURL())


class EditDatasheet(form.SubForm):

    hidden = ()

    @property
    def prefix(self):
        return self.context.__id__

    @property
    def fields(self):
        return form.Fields(self.context.__schema__).omit(*self.hidden)

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
                if schId in ct.hiddenFields:
                    form.hidden = ct.hiddenFields[schId]
                form.update()
                forms.append((schId, form))

        return forms


class ViewContent(view.View):
    view.pyramidView(
        'index.html', IContent,
        template = view.template('memphis.contenttype:templates/content.pt'))

    description = ''

    def update(self):
        try:
            ds = self.context.getDatasheet(schemas.IDublinCore)
            self.title = ds.title
            self.description = ds.description
        except KeyError:
            self.title = container.IContained(self.context).__name__
