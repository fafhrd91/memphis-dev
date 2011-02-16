import pytz, datetime
from zope import schema, interface
from zope.interface.common.mapping import IItemMapping
from zope.interface.common.mapping import IReadMapping, IEnumerableMapping

from memphis import storage, view
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('memphis.contenttype')


class IContained(interface.Interface):
    """ """

    __name__ = interface.Attribute('__name__')

    __parent__ = interface.Attribute('__parent__')


class IReadContainer(IItemMapping, IReadMapping, IEnumerableMapping):
    """Readable containers that can be enumerated."""


class IWriteContainer(interface.Interface):
    """An interface for the write aspects of a container."""

    def __setitem__(name, object):
        """Add the given `object` to the container under the given name."""

    def __delitem__(name):
        """Delete the named object from the container."""


class IContainer(IReadContainer, IWriteContainer):
    """Readable and writable content container."""


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

    hiddenFields = interface.Attribute('List of hidden fields')

    def __call__(**kw):
        """ create item """


class IFactoryProvider(interface.Interface):
    """ IFactory provider """

    def __iter__():
        """ factories iterator """

    def get(name, default=None):
        """ get factory by name """


class INameChooser(interface.Interface):
    """ adapter for (container, object) """

    def checkName(name):
        """ check name """

    def chooseName(name):
        """ choose name """


# basic dublin core
class IDCDescriptive(interface.Interface):
    """Basic descriptive meta-data properties"""

    title = schema.TextLine(
        title = u'Title',
        description=u"The first unqualified Dublin Core 'Title' element value."
        )

    description = schema.Text(
        title = u'Description',
        description = u"The first unqualified Dublin Core "\
            "'Description' element value.",
        )


class IDCTimes(interface.Interface):
    """Time properties"""

    created = schema.Datetime(
        title = u'Creation Date',
        description = u"The date and time that an object is created.",
        default = datetime.datetime.now(pytz.utc),
        required = False
        )

    modified = schema.Datetime(
        title = u'Modification Date',
        description = u"The date and time that the object "\
            "was last modified in a meaningful way.",
        default = datetime.datetime.now(pytz.utc),
        required = False
        )


# content system
class IContent(IDCDescriptive, IDCTimes):
    """ behavior interface for content types """

    title = schema.TextLine(
        title = _(u'Title'),
        description = _(u'Item title.'),
        default = u'',
        missing_value = u'',
        required = True)

    description = schema.Text(
        title = _(u'Description'),
        description = _(u'Brief summary of your content item.'),
        default = u'',
        missing_value = u'',
        required = False)

    type = schema.TextLine(
        title = _(u'Type'),
        description = _(u'Content Type Name'),
        required = True)

    created = schema.Datetime(
        title = _('Creation Date'),
        description = _("The date and time that an object is created."),
        required = False)

    modified = schema.Datetime(
        title = _('Modification Date'),
        description = _("The date and time that the object was "
                        "last modified in a meaningful way."),
        required = False)


class IContentContained(IContained):
    """ content contained """


class IContentContainer(IContainer):
    """ container for content """


class IContentTypeSchema(interface.Interface):
    """ schema for content type """
    storage.schema('memphis.contenttype')

    title = schema.TextLine(
        title = _('Title'),
        description = _('Content Type Title'),
        required = True)

    description = schema.Text(
        title = _('Description'),
        description = _('Content Type Description'),
        required = False)

    global_allow = schema.Bool(
        title = _('Global allow'),
        default = True,
        required = False)

    schemas = schema.Tuple(
        title = _(u'Schemas'),
        description = _(u'Content type schemas'),
        value_type = schema.TextLine(),
        default = (),
        required = True)

    hiddenFields = schema.Dict(
        title = u'Hidden fields',
        default = {},
        required = True)

    behaviors = schema.Tuple(
        title = _(u'Behaviors'),
        description = _(u'Content type behaviors'),
        value_type = schema.TextLine(),
        default = (),
        required = True)

    behaviorActions = schema.List(
        title = u'Behavior actions',
        default = [],
        required = True)

    widgets = schema.Dict(
        title = u'Widgets',
        default = {},
        required = True)


class IContentType(IFactory):
    """ content type """

    def __call__(**datasheets):
        """ create content """


class IContentTypesConfiglet(IContainer):
    """ configlet """

    
class ISchemaType(storage.ISchema):
    """ type """


class IBehaviorType(storage.ISchema):
    """ content type behavior """


# application root
class IRoot(IContent, IContentContainer, IContained, view.INavigationRoot):
    """ root """


# add form
class IAddContentForm(interface.Interface):
    """ content ad form """
