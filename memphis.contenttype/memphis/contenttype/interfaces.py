from zope import schema, interface
from memphis import storage, container, view
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('memphis.contenttype')


class WrongContentType(Exception):
    """ wrong content type """


class IItem(interface.Interface):
    """ Simple item """

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


class IContentContainer(container.ISimpleContainer):
    """ container for content """


class IContent(IItem):
    """ behavior interface for content types """

    type = schema.TextLine(
        title = _(u'Type'),
        description = _(u'Content Type Name'),
        required = True)


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

    schemaFields = schema.Dict(
        title = u'Schema fields',
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

    context = interface.Attribute('Context')

    def __bind__(context):
        """ bind to context """

    def add(content, name=''):
        """ add content to container """

    def checkObject(container, name, content):
        """ check content in container """

    def create(*datasheets):
        """ create content """

    def isAdable():
        """ addable in context """

    def isAvailable():
        """ available in context """

    def listContainedTypes(checkAvailability=True):
        """ list availabel content types allowed for adding """


class IBoundContentType(interface.Interface):
    """ bound content type """


class IContentTypeChecker(interface.Interface):
    """ check if content type withing context
    factory mwthod should accept 2 parameters: contenttype and context """

    def check():
        """ check """


class IContentTypeType(interface.interfaces.IInterface):
    """ content type type """


class IContentTypesConfiglet(interface.Interface):
    """ configlet """

    
class ISchemaType(storage.ISchema):
    """ type """


class IBehaviorType(storage.ISchema):
    """ content type behavior """


# application root
class IRoot(IContentContainer, view.IRoot):
    """ root """
