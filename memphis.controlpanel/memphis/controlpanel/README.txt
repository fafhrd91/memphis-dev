=============
Control Panel
=============

Package helps simplify creation site configuration configlet.

    >>> from zope import schema, interface
    >>> from memphis import controlpanel

Configlet
---------

Each configlet has to be part os category, but this is required only
for UI::

    >>> cat = controlpanel.registerCategory('testcategory')

    >>> cp = controlpanel.getControlPanel()
    >>> cp
    ControlPanel

    >>> cp['testcategory']
    Category <testcategory>
    
    >>> cp['testcategory'] is cat
    True

    >>> cp['unknown']
    Traceback (most recent call last):
    ...
    KeyError: 'unknown'

Can't register same category:

    >>> cat = controlpanel.registerCategory('testcategory')
    Traceback (most recent call last):
    ...
    KeyError: 'testcategory'

There are some predefined categories:

    >>> [cat for cat in cp.keys() if cat != 'testcategory']
    ['default', 'principals', 'ui', 'system']

You can apply marker interface to category:

    >>> class IMyCategory(interface.Interface):
    ...     pass

    >>> cat = controlpanel.registerCategory('mycategory', IMyCategory)
    >>> IMyCategory.providedBy(cp['mycategory'])
    True


Configlet registration requires schema object:

    >>> class IMyConfiglet(interface.Interface):
    ...     
    ...     title = schema.TextLine(
    ...         title = u'Title',
    ...         default = u'Not set')
    ...     
    ...     showNavigation = schema.Bool(
    ...         title = u'Show navigation',
    ...         default = False)

Thats it, but configlet can implements behavior:

    >>> class MyConfiglet(object):
    ...     
    ...     def isNavigationVisible(self):
    ...         return self.showNavigation

Now let's register configlet in control panel. To specify configlet
category you should prefix configlet name with category name divided
by ``.`` and you have to set category::

    >>> configlet = controlpanel.registerConfiglet(
    ...     'coolconfiglet', IMyConfiglet, MyConfiglet)
    Traceback (most recent call last):
    ...
    ValueError: Category name is required.

    >>> configlet = controlpanel.registerConfiglet(
    ...     'mycategory.coolconfiglet', IMyConfiglet, MyConfiglet)

    >>> configlet
    <memphis.controlpanel.configlettype.Configlet<coolconfiglet> ...>

    >>> configlet.__name__
    'coolconfiglet'

and you can't register configlet with same name:

    >>> configlet = controlpanel.registerConfiglet(
    ...     'mycategory.coolconfiglet', IMyConfiglet, MyConfiglet)
    Traceback (most recent call last):
    ...
    KeyError: 'coolconfiglet'

System generates new class for each configlet and register it in ZCA::

    >>> from zope import component
    >>> sm = component.getSiteManager()

    >>> sm.getUtility(IMyConfiglet)
    <memphis.controlpanel.configlettype.Configlet<coolconfiglet> ...>

You can access schema fields:

    >>> configlet.title, configlet.showNavigation
    (u'Not set', False)

    >>> configlet.isNavigationVisible()
    False

You can change configlet attributes, but value should have right type:

    >>> configlet.title = 'not unicode string'
    Traceback (most recent call last):
    ...
    WrongType: ('not unicode string', <type 'unicode'>, 'title')


When you register configlet, system creates behavior for this configlet:

    >>> configlet.__behavior__
    <memphis.storage.behavior.Behavior object at ...>

but you can't apply this behavior more than once:

    >>> from memphis import storage
    >>> item = storage.insertItem(IMyConfiglet)
    Traceback (most recent call last):
    ...
    BehaviorException: Can't create more than one configlet: coolconfiglet

    >>> item = storage.insertItem()
    >>> storage.getBehavior(IMyConfiglet)(item)
    Traceback (most recent call last):
    ...
    RuntimeError: Configlet behavior can't be called directly.

There is configlet method `isAvailable`, you can override it
and do not show configlet in UI in some situations. Configlet is available
by default.

    >>> configlet.isAvailable()
    True


Views
-----

System registers `/setting/*traverse` pyramid rout and register default
view for controlpanel:

    >>> from memphis import view
    >>> from pyramid.testing import DummyRequest

    >>> print view.renderView('index.html', cp, DummyRequest())
    200 OK
    Content-Type: text/html; charset=UTF-8
    Content-Length: 574
    ...
    <a href="http://example.com/settings/mycategory/coolconfiglet/"></a>
    ...
    </div>


System automaticly generate 'index.html' form based on configlet schema:

    >>> print view.renderView('index.html', configlet, DummyRequest())
    200 OK
    Content-Type: text/html; charset=UTF-8
    Content-Length: 1911
    ...
     <form action="http://example.com" name="configlet" id="configlet" method="post" enctype="multipart/form-data">
    ...
    </form>
    ...
    </div>

    >>> resp = view.renderView(
    ...     'index.html', configlet,
    ...     DummyRequest(params={'configlet.buttons.apply': u'Apply',
    ...                          'configlet.widgets.title': u'TTW modified',
    ...                          'configlet.widgets.showNavigation': "true"}))

    >>> configlet.title, configlet.showNavigation
    (u'TTW modified', True)

