====================
Memphis controlpanel
====================

It's very easy to use persistent utilities for storing data. But
persistent is the problem. Whole site would be broken if user removes
addon without unregistereing persistent utilities. Memphis controlpanel
solves this problem.

First of all let's define configuration schema::

    >>> from zope import interface, schema, component

    >>> class IMyConfiglet(interface.Interface):
    ...     
    ...     title = schema.TextLine(
    ...         title = u'Title',
    ...         default = u'test title',
    ...         required = True)
    ...     
    ...     description = schema.Text(
    ...         title = u'Description',
    ...         required = False)
    ...     
    ...     data = interface.Attribute('Data')


Now lets register configlet::

    >>> from memphis import controlpanel

    >>> controlpanel.registerConfiglet(
    ...     'myconfiglet', IMyConfiglet,
    ...     title = 'My configlet')


Configlet availabe as utility::

    >>> cl = component.getUtility(IMyConfiglet)

    >>> IMyConfiglet.providedBy(cl)
    True

    >>> cl.title
    u'test title'

Configlet automaticly validates value::

    >>> cl.title = 'test'
    Traceback (most recent call last):
    ...
    WrongType: ('test', <type 'unicode'>, 'title')

    >>> cl.title = u'test'
    >>> cl.title
    u'test'

Configlet uses default value if there is no value set::

    >>> del cl.title
    >>> cl.title
    u'test title'


SimpleItem attributes

    >>> cl.id, cl.getId(), cl.Title(), cl.__name__
    ('myconfiglet', 'myconfiglet', 'My configlet', 'myconfiglet')


Add-on
======

Memphis controlpanel uses zope component registry as addon, so it just
zca registry and developer uses this registry to register his
adapters, utilities, views and everything else. All memphis.controlpanel
does is just adding this registry to site manager.

Code looks like this::

    >>> from memphis import config

    >>> register = config.registry('my.super.addon', addon=True)

That's it, now this registry available as add-on in "Add-ons" configlet.
To use this registry with memphis base registrations you should use
`config.registerIn('my.super.addon')` directive. Remember, order
doesn't matter, if module has `config.registerIn` directive all registrations
from this module go to this registry.

Also it's possible to use `z3c.baseregistry` package for zcml registrations.
zcml looks like this::

   <configure xmlns="http://namespaces.zope.org/zope">

     <include package="z3c.baseregistry" file="meta.zcml">

     <registerIn registry="path-to-your-module-with-registry.registry">
        <!-- here goes all registrations like
             <adapter/>,<utility/>, <browser:page/>, etc -->
        ...
     </registerIn>
   </configure>
