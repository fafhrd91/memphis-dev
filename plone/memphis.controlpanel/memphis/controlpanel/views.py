""" control panel views 

    >>> from memphis import controlpanel
    >>> from zope import component, interface, schema
    
    >>> class IConfig(interface.Interface):
    ...     test = schema.TextLine(
    ...         title = u'Test',
    ...         default = u'default text')

    >>> controlpanel.registerConfiglet(
    ...     'myconfig', IConfig,
    ...     title = 'My config',
    ...     description = 'My config description')

    >>> config = component.getUtility(IConfig)

'++cp++configletname' traverser

    >>> from OFS.Application import Application
    >>> from OFS.SimpleItem import SimpleItem
    >>> item = SimpleItem('site')
    >>> item.id = 'site'
    >>> interface.directlyProvides(item, ISiteRoot)

    >>> from Testing.makerequest import makerequest
    >>> app = makerequest(Application())
    >>> item = item.__of__(app)
    >>> request = item.REQUEST

    >>> traverser = component.getMultiAdapter((item, request), ITraversable, 'cp')

    >>> config = traverser.traverse('unknown', ())
    Traceback (most recent call last):
    ...
    LocationError: ...

    >>> config = traverser.traverse('myconfig', ())
    >>> config.__id__ == 'myconfig'
    True
    >>> config.__schema__ is IConfig
    True

    >>> view = component.getMultiAdapter((config, request), name='index.html')

    >>> view()
    Traceback (most recent call last):
    ...
    Unauthorized: Unauthorized()

    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> from zope.publisher.interfaces.browser import IBrowserRequest
    >>> from Products.statusmessages.interfaces import IStatusMessage
    >>> from Products.statusmessages.adapter import StatusMessage
    >>> from memphis import config as capi
    >>> capi.registerAdapter(StatusMessage, (IBrowserRequest,), IStatusMessage)
    >>> interface.alsoProvides(request, IAttributeAnnotatable)
    >>> from zope.annotation.attribute import AttributeAnnotations
    >>> component.provideAdapter(AttributeAnnotations)

    >>> class FakeSecurityManager(object):
    ...     def checkPermission(self, *args):
    ...         return True

    >>> from AccessControl.SecurityManagement import setSecurityManager
    >>> setSecurityManager(FakeSecurityManager())

    >>> view = view.factory(config, request)

    >>> from memphis import form
    >>> form.IForm.providedBy(view)
    True

    >>> view.label
    'My config'
    >>> view.description
    'My config description'

    >>> view.update()
    >>> print view.render()
    <div class="form-edit">
    ...
    <input id="form-widgets-test" name="form.widgets.test" class="text-widget required textline-field" value="default text" type="text" />
    ...
    </div>

    >>> config.test
    u'default text'

    >>> request.form.update(
    ...     {'form.widgets.test': u'test text',
    ...      'form.buttons.save': u'Save'})

    >>> view.update()

    >>> config.test
    u'test text'

    >>> view.cancelURL()
    'http://foo/site/plone_control_panel'
    
"""

from zope import interface
from zope.component import queryUtility
from zope.location import LocationProxy
from zope.location.interfaces import LocationError
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from Acquisition import Implicit
from AccessControl import Unauthorized, getSecurityManager
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from memphis import config, view, form
from memphis.controlpanel.interfaces import IConfiglet


view.registerLayout(
    '', IConfiglet,
    klass = view.ZopeLayout,
    template = ViewPageTemplateFile(
        view.path('memphis.controlpanel:templates/layout-prefs.pt'))
)


def CheckPermission(factory):
    def callView(context, request):
        if getSecurityManager().checkPermission(context.permission, context):
            return factory(context, request)

        raise Unauthorized()

    return callView


class LocationProxy(LocationProxy, Implicit):
    """ location proxy with acquisition """


class ConfigletView(form.EditForm, view.View):
    view.zopeView('index.html', IConfiglet,
                  default = True,
                  decorator = CheckPermission)

    @property
    def fields(self):
        return form.Fields(self.context.__schema__)

    @property
    def label(self):
        return self.context.__title__

    @property
    def description(self):
        return self.context.__description__

    def cancelURL(self):
        return '%s/plone_control_panel'%self.context.__parent__.absolute_url()


class ControlpanelTraversable(object):
    interface.implements(ITraversable)
    config.adapts(ISiteRoot, IDefaultBrowserLayer, name='cp')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        configlet = queryUtility(IConfiglet, name)
        if configlet is None:
            raise LocationError(self.context, name)

        return LocationProxy(configlet, self.context).__of__(self.context)
