import pyramid.url
from webob.exc import HTTPFound

from zope import interface
from zope.component import getUtility, queryUtility, getSiteManager

from memphis import form, config, view, storage

from memphis.contenttype import pagelets
from memphis.contenttype.form import AddContentForm
from memphis.contenttype.interfaces import \
    _, IContent, IContentType, IDCDescriptive, IAddContentForm, IEditContentForm


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
    interface.implements(IAddContentForm)
    view.pyramidView('', IContentType)

    fields = form.Fields()
    validate = AddContentForm.validate

    @property
    def label(self):
        return 'Add content: %s'%self.context.title

    @property
    def description(self):
        return self.context.description

    def listInlineForms(self):
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

        forms.extend(super(AddContent, self).listInlineForms())
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
    interface.implements(IEditContentForm)
    view.pyramidView('edit.html', IContent)

    fields = form.Fields()

    label = 'Modify content'

    def listInlineForms(self):
        context = self.context
        ct = IContentType(context)

        forms = []
        for schId in ('content.item',) + ct.schemas:
            schema = storage.querySchema(schId)
            if schema is not None:
                ds = context.getDatasheet(schId, True)
                eform = EditDatasheet(ds, self.request, self)
                eform.mode = self.mode
                if eform.mode == form.IDisplayMode:
                    interface.directlyProvides(eform, form.IDisplayForm)
                if schId == 'content.item':
                    eform.hidden = 'type', 'modified', 'created'
                if schId in ct.hiddenFields:
                    eform.hidden = ct.hiddenFields[schId]
                if schId in ct.widgets:
                    eform.widgetFactories = ct.widgets[schId]
                eform.update()
                forms.append((schId, eform))

        forms.extend(super(EditContent, self).listInlineForms())
        return forms


class ViewContent(EditContent):
    interface.implements(form.IDisplayForm)
    view.pyramidView('index.html', IContent)

    mode = form.IDisplayMode
    ignoreRequest = True

    def update(self):
        dc = IDCDescriptive(self.context)
        self.label = dc.title
        self.description = dc.description

        super(ViewContent, self).update()


class ContentActions(view.Pagelet):
    view.pagelet(
        pagelets.IContentActions,
        template = view.template('memphis.contenttype:templates/actions.pt'))

    def update(self):
        adapters = getSiteManager().adapters

        self.actions = [action for name, action in adapters.lookupAll(
                (interface.providedBy(self.context),), view.IAction)]
        self.actions.sort(key = lambda a: a.weight)
