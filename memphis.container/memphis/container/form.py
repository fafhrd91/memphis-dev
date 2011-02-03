""" 

$Id: form.py 4729 2011-02-03 05:26:47Z nikolay $
"""
from webob.exc import HTTPFound
from pyramid.exceptions import NotFound

from zope import schema, interface, event
from zope.lifecycleevent import ObjectCreatedEvent

from memphis import config, view
from memphis.form import form, field, button, validator

from memphis.container import interfaces

_ = interfaces._


class ContentNameError(schema.ValidationError):
    __doc__ = _(u'Content name already in use.')

    def __init__(self, msg):
        self.__doc__ = msg


class AddFormNameValidator(validator.InvariantsValidator):
    config.adapts(
        interface.Interface,
        interface.Interface,
        interfaces.IAddContentForm,
        interface.Interface,
        interface.Interface)

    def validate(self, data):
        if not self.view.nameAllowed():
            return super(AddFormNameValidator, self).validate(data)

        errors = []
        container = self.view.context.__parent__

        # check content name
        chooser = interfaces.INameChooser(container)

        name = self.view.getName(None)
        if name or interfaces.IEmptyNamesNotAllowed.providedBy(container):
            try:
                chooser.checkName(name, None)
            except Exception, err:
                error = ContentNameError(unicode(err))
                errors.append(error)
                self.view.nameError = err

        return tuple(errors) + super(AddFormNameValidator, self).validate(data)


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
        return field.Fields(self.context.schema, omitReadOnly=True)

    @property
    def label(self):
        return self.context.title

    @property
    def description(self):
        return self.context.description

    def create(self, data):
        return self.context(**data)

    def getName(self, object=None):
        return self.request.params.get('add_input_name', '')

    def add(self, object):
        name = self.getName(object)
        container = self.context.__parent__

        chooser = interfaces.INameChooser(container)

        name = chooser.chooseName(name, object)
        container[name] = object

        self.addedObject = container[name]
        return self.addedObject

    def createAndAdd(self, data):
        obj = self.create(data)
        event.notify(ObjectCreatedEvent(obj))
        self.add(obj)
        return obj

    @button.buttonAndHandler(_(u'Add'), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()

        if errors:
            errors = [error for error in errors
                      if not error.error.__class__ == ContentNameError]

            view.addStatusMessage(
                self.request, [self.formErrorsMessage] + errors, 'formError')
        else:
            obj = self.createAndAdd(data)

            if obj is not None:
                self.addedObject = obj
                self.finishedAdd = True
                raise HTTPFound(location = self.nextURL())

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        view.addStatusMessage(self.request, self.formCancelMessage)
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
