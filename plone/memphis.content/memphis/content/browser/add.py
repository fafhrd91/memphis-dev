""" add content form, ++content++${typeinfo}"""
from webob.exc import HTTPFound

from Acquisition import aq_base, aq_parent
from Products.CMFCore.interfaces import ITypeInformation

from zope import schema, interface, event
from zope.component import getAdapter, queryUtility, getMultiAdapter
from zope.container.interfaces import INameChooser
from zope.location.interfaces import LocationError
from zope.traversing.interfaces import ITraversable
from zope.traversing.browser import absoluteURL
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from plone.app.content.interfaces import INameFromTitle

from memphis import config, view, form, content
from memphis.content.interfaces import _
from memphis.content.browser import interfaces, CheckPermission

from pagelets import IDatasheetForm
from interfaces import IAddContentForm
from datasheet import DatasheetEdit


class IShortName(interface.Interface):

    name = schema.TextLine(
        title = _('Short Name'),
        description = _("Should not contain spaces, underscores or mixed case. "
                        "Short Name is part of the item's web address."),
        required = False)


class AddContentForm(form.EditForm, view.View):
    interface.implements(IAddContentForm)
    view.zopeView('index.html', ITypeInformation,
                  default = True,
                  decorator = CheckPermission)

    prefix = 'content.add.'
    id = 'content-form-add'
    formCancelMessage = _(u'Content creation has been canceled.')

    @property
    def fields(self):
        return form.Fields(IShortName)

    @property
    def label(self):
        return self.context.title

    @property
    def description(self):
        return self.context.description

    def getContent(self):
        return None

    def listInlineForms(self):
        ct = self.context
        request = self.request

        forms = []
        datasheets = {}
        for schId in ct.schemas:
            schema = content.querySchema(schId)
            if schema is not None:
                ds = schema.Type()
                datasheets[schema.name] = ds

                form = DatasheetEdit(ds, request, self)

                #form = getMultiAdapter((ds, request), IDatasheetForm)
                #if schId in ct.widgets:
                #    form.widgetFactories = ct.widgets[schId]
                form.update()
                forms.append((schId, form))

        self.datasheets = datasheets

        forms.extend(super(AddContentForm, self).listInlineForms())
        return forms

    def create(self, data):
        return self.context.create(**data)

    def add(self, name, instance):
        container = aq_parent(self.context)

        chooser = getAdapter(container, INameChooser)
        name = chooser.chooseName(name, instance)
        
        instance._setId(name)
        id = container._setObject(name, aq_base(instance))
        
        return container[id]

    def createAndAdd(self, name, datasheets):
        obj = self.create(datasheets)
        return self.add(name, obj)

    @form.buttonAndHandler(_(u'Add'), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()

        if errors:
            view.addMessage(
                self.request, self.formErrorsMessage, 'formError')
        else:
            for form in self.subforms:
                data, errors = form.extractData(setErrors=False)
                form.applyChanges(data)

            obj = self.createAndAdd(data.get('name',''), self.datasheets)
            if obj is not None:
                raise HTTPFound(location = self.nextURL(obj))

    @form.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        view.addMessage(self.request, self.formCancelMessage)
        raise HTTPFound(location = self.cancelURL())

    def nextURL(self, obj):
        url = absoluteURL(obj, self.request)
        action = obj.__type__.getActionInfo('object/view')
        if action is not None:
            return '%s%s'%(url, action['url'])

        return url

    def cancelURL(self):
        return self.context.aq_parent.absolute_url()

    def nameAllowed(self):
        """Return whether names can be input by the user."""
        context = self.context.__parent__

        if IWriteContainer.providedBy(context):
            return not IContainerNamesContainer.providedBy(context)
        else:
            return False


class ContentTraversable(object):
    interface.implements(ITraversable)
    config.adapts(interface.Interface, IDefaultBrowserLayer, name='content')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        ti = queryUtility(ITypeInformation, name)

        if ti is None:
            raise LocationError(self.context, name)

        return ti.__of__(self.context)
