""" 

$Id: namechooser.py 4729 2011-02-03 05:26:47Z nikolay $
"""
from zope import interface
from memphis import config
from interfaces import _, IContainer, INameChooser


class NameChooser(object):
    config.adapts(IContainer)
    interface.implements(INameChooser)

    def __init__(self, context):
        self.context = context

    def checkName(self, name, object):
        """See memphis.container.interfaces.INameChooser

        We create and populate a dummy container

        >>> from memphis import storage
        >>> from memphis.container.interfaces import ISimpleContainer
        >>> container = IContainer(storage.insertItem(ISimpleContainer))

        >>> container['foo'] = storage.insertItem()
        >>> from memphis.container.namechooser import NameChooser

        An invalid name raises a ValueError:

        >>> NameChooser(container).checkName('', object())
        Traceback (most recent call last):
        ...
        ValueError: An empty name was provided. Names cannot be empty.

        >>> NameChooser(container).checkName('+foo', object())
        Traceback (most recent call last):
        ...
        ValueError: Names cannot begin with '+' or '@' or contain '/'

        A name that already exists raises a KeyError:

        >>> NameChooser(container).checkName('foo', object())
        Traceback (most recent call last):
        ...
        KeyError: u'The given name is already being used'

        A name must be a string or unicode string:

        >>> NameChooser(container).checkName(2, object())
        Traceback (most recent call last):
        ...
        TypeError: ('Invalid name type', <type 'int'>)

        A correct name returns True:

        >>> NameChooser(container).checkName('2', object())
        True

        #We can reserve some names by providing a IReservedNames adapter
        #to a container:

        #>>> from zope.container.interfaces import IContainer
        #>>> class ReservedNames(object):
        #...     zope.component.adapts(IContainer)
        #...     zope.interface.implements(IReservedNames)
        #...
        #...     def __init__(self, context):
        #...         self.reservedNames = set(('reserved', 'other'))

        #>>> zope.component.getSiteManager().registerAdapter(ReservedNames)

        #>>> NameChooser(container).checkName('reserved', None)
        #Traceback (most recent call last):
        #...
        #NameReserved: reserved
        """

        if isinstance(name, str):
            name = unicode(name)
        elif not isinstance(name, unicode):
            raise TypeError("Invalid name type", type(name))

        if not name:
            raise ValueError(
                _("An empty name was provided. Names cannot be empty.")
                )

        if name[:1] in '+@' or '/' in name:
            raise ValueError(
                _("Names cannot begin with '+' or '@' or contain '/'")
                )

        #reserved = IReservedNames(self.context, None)
        #if reserved is not None:
        #    if name in reserved.reservedNames:
        #        raise NameReserved(name)

        if name in self.context:
            raise KeyError(
                _("The given name is already being used")
                )

        return True


    def chooseName(self, name, object):
        """See zope.container.interfaces.INameChooser

        The name chooser is expected to choose a name without error

        We create and populate a dummy container

        >>> from memphis import storage
        >>> from memphis.container.interfaces import ISimpleContainer
        >>> container = IContainer(storage.insertItem(ISimpleContainer))

        >>> container['foobar.old'] = storage.insertItem()

        the suggested name is converted to unicode:

        >>> NameChooser(container).chooseName('foobar', object())
        u'foobar'

        If it already exists, a number is appended but keeps the same extension:

        >>> NameChooser(container).chooseName('foobar.old', object())
        u'foobar-2.old'

        Bad characters are turned into dashes:

        >>> NameChooser(container).chooseName('foo/foo', object())
        u'foo-foo'

        If no name is suggested, it is based on the object type:

        >>> NameChooser(container).chooseName('', [])
        u'list'

        If name is not convertible to unicode use empty name
        >>> NameChooser(container).chooseName(
        ...    '\xc3\x91\xc2\x82\xc3\x90\xc2\xb5\xc3\x91\xc2\x81\xc3\x91\xc2\x82',
        ...     object())
        u'object'

        """
        container = self.context

        # convert to unicode and remove characters that checkName does not allow
        try:
            name = unicode(name)
        except:
            name = u''
        name = name.replace('/', '-').lstrip('+@')

        if not name:
            name = unicode(object.__class__.__name__)

        # for an existing name, append a number.
        # We should keep client's os.path.extsep (not ours), we assume it's '.'
        dot = name.rfind('.')
        if dot >= 0:
            suffix = name[dot:]
            name = name[:dot]
        else:
            suffix = ''

        n = name + suffix
        i = 1
        while n in container:
            i += 1
            n = name + u'-' + unicode(i) + suffix

        # Make sure the name is valid.  We may have started with something bad.
        self.checkName(n, object)

        return n
