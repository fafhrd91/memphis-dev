""" 

$Id: location.py 4729 2011-02-03 05:26:47Z nikolay $
"""
from zope.interface import providedBy
from zope.interface.declarations import getObjectSpecification
from zope.interface.declarations import ObjectSpecification
from zope.interface.declarations import ObjectSpecificationDescriptor


class DecoratorSpecificationDescriptor(ObjectSpecificationDescriptor):
    """Support for interface declarations on decorators

    >>> from zope.interface import *
    >>> class I1(Interface):
    ...     pass
    >>> class I2(Interface):
    ...     pass
    >>> class I3(Interface):
    ...     pass
    >>> class I4(Interface):
    ...     pass

    >>> class D1(LocationWrapper):
    ...   implements(I1)


    >>> class D2(LocationWrapper):
    ...   implements(I2)

    >>> class X(object):
    ...   implements(I3)

    >>> x = X()
    >>> directlyProvides(x, I4)

    Interfaces of X are ordered with the directly-provided interfaces first

    >>> [interface.getName() for interface in list(providedBy(x))]
    ['I4', 'I3']

    When we decorate objects, what order should the interfaces come
    in?  One could argue that decorators are less specific, so they
    should come last.

    >>> [interface.getName() for interface in list(providedBy(D1(x)))]
    ['I4', 'I3', 'I1']

    >>> [interface.getName() for interface in list(providedBy(D2(D1(x))))]
    ['I4', 'I3', 'I1', 'I2']

    SpecificationDecorators also work with old-style classes:

    >>> class X:
    ...   implements(I3)

    >>> x = X()
    >>> directlyProvides(x, I4)

    >>> [interface.getName() for interface in list(providedBy(x))]
    ['I4', 'I3']

    >>> [interface.getName() for interface in list(providedBy(D1(x)))]
    ['I4', 'I3', 'I1']

    >>> [interface.getName() for interface in list(providedBy(D2(D1(x))))]
    ['I4', 'I3', 'I1', 'I2']
    """
    def __get__(self, inst, cls=None):
        if inst is None:
            return getObjectSpecification(cls)
        else:
            provided = providedBy(inst.__object__)

            # Use type rather than __class__ because inst is a proxy and
            # will return the proxied object's class.
            cls = type(inst)
            return ObjectSpecification(provided, cls)

    def __set__(self, inst, value):
        raise TypeError("Can't set __providedBy__ on a decorated object")


class LocationWrapper(object):
    """ readonly location wrapper

    >>> class Content(object):
    ...     attr = 'Test'
    ...     def __call__(self):
    ...         return 'Called'

    >>> content = Content()

    >>> location = LocationWrapper(content, name='newlocation')

    >>> location.attr
    'Test'
    >>> location()
    'Called'
    >>> location.__name__
    'newlocation'
    >>> location.__providedBy__ = None
    Traceback (most recent call last):
    ...
    TypeError: Can't set __providedBy__ on a decorated object

    """

    def __init__(self, object, parent=None, name=''):
        self.__object__ = object
        self.__parent__ = parent
        self.__name__ = name

    def __call__(self, *args, **kw):
        return self.__object__(*args, **kw)

    def __getattr__(self, name):
        return getattr(self.__object__, name)

    __providedBy__ = DecoratorSpecificationDescriptor()
