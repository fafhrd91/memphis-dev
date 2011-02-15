import pyramid.url
from webob.exc import HTTPFound

from zope import interface
from zope.component import getUtility, queryUtility, getSiteManager

from memphis import form, config, view, storage

from memphis.contenttype import pagelets
from memphis.contenttype.form import AddContentForm
from memphis.contenttype.interfaces import \
    _, IContent, IContentType, IDCDescriptive


config.action(
    view.registerDefaultView,
    'index.html', IContent)


config.action(
    view.registerActions,
    ('index.html', IContent, 
     _('View'), _('View content.'), 10),
    ('edit.html', IContent, 
     _('Edit'), _('Edit content.'), 20))


class AddContent(form.EditForm, AddContentForm, view.View):
    view.pyramidView('', IContentType)

    fields = form.Fields()
    validate = AddContentForm.validate

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
        for schId in ('content.item',) + tuple(self.context.schemas):
            schema = queryUtility(storage.ISchema, schId)
            if schema is not None:
                ds = schema.Type()
                datasheets[schema.name] = ds
                form = EditDatasheet(ds, self.request, self)
                if schId == 'content.item':
                    form.hidden = 'type', 'modified', 'created'
                if schId in ct.hiddenFields:
                    form.hidden = ct.hiddenFields[schId]
                if schId in ct.widgets:
                    form.widgetFactories = ct.widgets[schId]
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
    widgetFactories = {}

    @property
    def prefix(self):
        return self.context.__id__

    @property
    def fields(self):
        fields = form.Fields(self.context.__schema__).omit(*self.hidden)
        for name, widget in self.widgetFactories.items():
            fields[name].widgetFactory = widget

        return fields

    @property
    def label(self):
        if self.context.__id__ != 'content.item':
            return self.context.__title__

    @property
    def description(self):
        if self.context.__id__ != 'content.item':
            return self.context.__description__


class EditContent(form.EditForm, view.View):
    view.pyramidView('edit.html', IContent)

    fields = form.Fields()

    label = 'Modify content'

    def listWrappedForms(self):
        ct = IContentType(self.context)

        forms = []
        for schId in ('content.item',) + ct.schemas:
            schema = queryUtility(storage.ISchema, schId)
            if schema is not None:
                ds = schema.getDatasheet(self.context.oid)
                form = EditDatasheet(ds, self.request, self)
                if schId == 'content.item':
                    form.hidden = 'type', 'modified', 'created'
                if schId in ct.hiddenFields:
                    form.hidden = ct.hiddenFields[schId]
                if schId in ct.widgets:
                    form.widgetFactories = ct.widgets[schId]
                form.update()
                forms.append((schId, form))

        return forms


class ViewContent(view.View):
    view.pyramidView(
        'index.html', IContent,
        template = view.template('memphis.contenttype:templates/content.pt'))

    def update(self):
        dc = IDCDescriptive(self.context)
        self.title = dc.title
        self.description = dc.description


class ContentActions(view.Pagelet):
    view.pagelet(
        pagelets.IContentActions,
        template = view.template('memphis.contenttype:templates/actions.pt'))

    def update(self):
        adapters = getSiteManager().adapters

        actions = []
        for name, action in adapters.lookupAll(
            (interface.providedBy(self.context),), view.IAction):
            actions.append(action)

        self.actions = actions
