from zope import schema, interface
from memphis import storage, container, view
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('memphis.contenttype')


class IContent(interface.Interface):
    """ behavior interface for content types """

    type = schema.TextLine(
        title = _(u'Type'),
        description = _(u'Content Type Name'),
        required = True)


class IContentContainer(container.ISimpleContainer):
    """ container for content """


class IContentTypeSchema(interface.Interface):
    """ schema for content type """
    storage.schema('memphis.contenttype')

    title = schema.TextLine(
        title = _(u'Title'),
        description = _(u'Content Type Title'),
        required = True)

    description = schema.Text(
        title = _(u'Description'),
        description = _(u'Content Type Description'),
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
class IRoot(IContentContainer, view.IRoot, container.IContained):
    """ root """
