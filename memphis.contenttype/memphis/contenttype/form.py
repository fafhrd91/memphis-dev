from webob.exc import HTTPFound
from pyramid import url
from pyramid.exceptions import NotFound

from zope import schema, interface, event
from zope.component import getMultiAdapter
from zope.lifecycleevent import ObjectCreatedEvent

from memphis import config, view, form
from memphis.contenttype import interfaces

_ = interfaces._


class AddContentForm(form.Form):
    interface.implements(interfaces.IAddContentForm)

    prefix = 'content.add.'
    id = 'content-forms-add'
    ignoreContext = True
    formCancelMessage = _(u'Content creation has been canceled.')

    nameError = None
    addedObject = None
    factory = None

    @property
    def fields(self):
        return form.Fields(self.context.schema, omitReadOnly=True).omit(
            *self.context.hiddenFields)

    @property
    def label(self):
        return self.context.title

    @property
    def description(self):
        return self.context.description

    def validate(self, data):
        errors = super(AddContentForm, self).validate(data)

        if not self.nameAllowed():
            return errors

        container = interfaces.IContainer(self.context.__parent__)

        # check content name
        chooser = getMultiAdapter(
            (container, self.context), interfaces.INameChooser)

        name = self.getName(None)
        if name or interfaces.IEmptyNamesNotAllowed.providedBy(container):
            try:
                chooser.checkName(name)
            except Exception, err:
                error = form.CustomValidationError(unicode(err))
                errors.append(error)
                self.nameError = err

        return errors

    def create(self, data):
        return self.context(**data)

    def getName(self, object=None):
        return self.request.params.get('add_input_name', '')

    def add(self, object):
        name = self.getName(object)
        container = interfaces.IContainer(self.context.__parent__)

        chooser = getMultiAdapter((container, object), interfaces.INameChooser)

        name = chooser.chooseName(name)
        container[name] = object

        self.addedObject = container[name]
        return self.addedObject

    def createAndAdd(self, data):
        obj = self.create(data)
        event.notify(ObjectCreatedEvent(obj))
        self.add(obj)
        return obj

    @form.buttonAndHandler(_(u'Add'), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()

        if errors:
            view.addMessage(
                self.request, (self.formErrorsMessage,) + errors, 'formError')
        else:
            obj = self.createAndAdd(data)

            if obj is not None:
                self.addedObject = obj
                self.finishedAdd = True
                raise HTTPFound(location = self.nextURL())

    @form.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        view.addMessage(self.request, self.formCancelMessage)
        raise HTTPFound(location = self.cancelURL())

    def nextURL(self):
        #viewName = queryMultiAdapter(
        #    (self._addedObject, self.request), IContentViewView)
        #if viewName is not None:
        #    return '%s/%s'%(
        #absoluteURL(self._addedObject, self.request), viewName.name)
        #else:
        #return self.request.resource_url('../../')
        return '../../'

    def cancelURL(self):
        return self.request.resource_url(self.context.__parent__)

    def nameAllowed(self):
        """Return whether names can be input by the user."""
        context = self.context.__parent__

        if interfaces.IWriteContainer.providedBy(context):
            return not interfaces.IContainerNamesContainer.providedBy(context)
        else:
            return False
