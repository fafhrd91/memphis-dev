
""" memphis.preferences interfaces

$Id: interfaces.py 11800 2011-01-31 04:36:54Z fafhrd91 $
"""
from zope import schema, interface
from pyramid.i18n import TranslationStringFactory

from memphis import storage, view

_ = TranslationStringFactory('memphis.preferences')


class UnboundPreferenceGroup(Exception):
    """ Prefernce group is not bound to principal """


class IPreference(interface.Interface):
    """A group of preferences.

    This component represents a logical group of preferences. The preferences
    contained by this group is defined through the schema. The group has also
    a name by which it can be accessed.

    The fields specified in the schema *must* be available as attributes and
    items of the group instance. It is up to the implementation how this is
    realized, however, most often one will implement __setattr__ and
    __getattr__ as well as the common mapping API.

    The reason all the API fields are doubly underlined is to avoid name clashes.
    """

    __id__ = schema.TextLine(
        title = u"Id",
        description = u"The id of the group.",
        required = True)

    __schema__ = schema.InterfaceField(
        title = u"Schema",
        description = u"Schema describing the preferences of the group.",
        required = False,
        readonly = True)

    __title__ = schema.TextLine(
        title = u"Title",
        description = u"The title of the group used in the UI.",
        required = True)

    __description__ = schema.TextLine(
        title = u"Description",
        description = u"The description of the group used in the UI.",
        required = False)

    __principal__ = interface.Attribute('Owner principal of preferences')

    def isAvailable():
        """ is group available for bound principal """

    def __bind__(principal=None, parent=None):
        """ bind preferences """


class IPreferenceCategory(interface.Interface):
    """A collection of preference groups.

    Objects providing this interface serve as groups of preference
    groups. This allows UIs to distinguish between high- and low-level
    prefernce groups.
    """


class IBound(interface.Interface):
    """ bound to context """

    __principal__ = interface.Attribute('Principal')


class IPreferences(view.INavigationRoot):
    """ root preferences behavior """
    storage.schema('memphis.preferences')

    principal = schema.TextLine(
        title = u'Principal id',
        required = True)
