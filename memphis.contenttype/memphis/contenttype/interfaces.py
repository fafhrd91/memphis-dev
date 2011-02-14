from zope import schema, interface
from memphis import storage, container, view
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('memphis.contenttype')


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
        description = u"The date and time that an object is created."
        )

    modified = schema.Datetime(
        title = u'Modification Date',
        description = u"The date and time that the object "\
            "was last modified in a meaningful way.",
        )


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


class IContentContainer(container.ISimpleContainer):
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

    behaviorActions = schema.Dict(
        title = u'Behavior actions',
        default = {},
        required = True)

    widgets = schema.Dict(
        title = u'Widgets',
        default = {},
        required = True)


class IContentType(container.IFactory):
    """ content type """

    def __call__(**datasheets):
        """ create content """


class IContentTypesConfiglet(container.IContainer):
    """ configlet """

    
class ISchemaType(storage.ISchema):
    """ type """


class IBehaviorType(storage.ISchema):
    """ content type behavior """


# application root
class IRoot(IContent, IContentContainer, 
            view.INavigationRoot, container.IContained):
    """ root """
