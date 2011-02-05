""" Container-related interfaces
"""
from memphis import storage
from zope import schema, interface
from zope.interface.common.mapping import IItemMapping
from zope.interface.common.mapping import IReadMapping, IEnumerableMapping
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('memphis.container')



class IContained(interface.Interface):
    """ """

    __name__ = interface.Attribute('__name__')

    __parent__ = interface.Attribute('__parent__')


class IReadContainer(IItemMapping, IReadMapping, IEnumerableMapping):
    """Readable containers that can be enumerated."""


class IWriteContainer(interface.Interface):
    """An interface for the write aspects of a container."""

    def __setitem__(name, object):
        """Add the given `object` to the container under the given name.

        Raises a ``TypeError`` if the key is not a unicode or ascii string.

        Raises a ``ValueError`` if the key is empty, or if the key contains
        a character which is not allowed in an object name.

        Raises a ``KeyError`` if the key violates a uniqueness constraint.

        The container might choose to add a different object than the
        one passed to this method.

        If the object doesn't implement `IContained`, then one of two
        things must be done:

        1. If the object implements `ILocation`, then the `IContained`
           interface must be declared for the object.

        2. Otherwise, a `ContainedProxy` is created for the object and
           stored.

        The object's `__parent__` and `__name__` attributes are set to the
        container and the given name.

        If the old parent was ``None``, then an `IObjectAddedEvent` is
        generated, otherwise, an `IObjectMovedEvent` is generated.  An
        `IContainerModifiedEvent` is generated for the container.

        If the object replaces another object, then the old object is
        deleted before the new object is added, unless the container
        vetos the replacement by raising an exception.

        If the object's `__parent__` and `__name__` were already set to
        the container and the name, then no events are generated and
        no hooks.  This allows advanced clients to take over event
        generation.

        """

    def __delitem__(name):
        """Delete the named object from the container.

        Raises a ``KeyError`` if the object is not found.

        If the deleted object's `__parent__` and `__name__` match the
        container and given name, then an `IObjectRemovedEvent` is
        generated and the attributes are set to ``None``. If the object
        can be adapted to `IObjectMovedEvent`, then the adapter's
        `moveNotify` method is called with the event.

        Unless the object's `__parent__` and `__name__` attributes were
        initially ``None``, generate an `IContainerModifiedEvent` for the
        container.

        If the object's `__parent__` and `__name__` were already set to
        ``None``, then no events are generated.  This allows advanced
        clients to take over event generation.

        """


class IContainer(IReadContainer, IWriteContainer):
    """Readable and writable content container."""


class ISimpleContained(IContained):
    """ simple contained """


class ISimpleContainer(IContainer):
    """ simple container """


# adding
class IEmptyNamesNotAllowed(interface.Interface):
    """ marker interface """


class IContainerNamesContainer(interface.Interface):
    """Containers that always choose names for their items."""


class IFactory(interface.Interface):

    name = interface.Attribute('Factory name')

    title = interface.Attribute('Title')

    description = interface.Attribute('Description')

    schema = interface.Attribute('Content schema')

    def __call__(**kw):
        """ create item """


class IFactoryVocabulary(schema.interfaces.IVocabulary):
    """ factories vocabulary """


class INameChooser(interface.Interface):
    """ adapter for (container, object) """

    def checkName(name):
        """ check name """

    def chooseName(name):
        """ choose name """


class IAddContentForm(interface.Interface):
    """ content ad form """


class IAction(interface.Interface):
    """ item action """

    name = interface.Attribute('Name')

    title = interface.Attribute('Title')

    description = interface.Attribute('Description')


# application root
class IRoot(IContainer):
    """ root """
