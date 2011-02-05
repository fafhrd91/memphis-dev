""" content type interfaces

$Id: interfaces.py 11771 2011-01-29 22:56:56Z fafhrd91 $
"""
from zope import schema, interface
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


class IContent(interface.Interface):
    """ marker interface for content types """


class IContentItem(IItem):
    """ marker interface for content types """


class IContainer(IItem):
    """ container for content """


class IContentTypeSchema(interface.Interface):
    """ content behavior schema """

    type = schema.TextLine(
        title = _(u'Type'),
        description = _(u'Content Type Name'),
        required = True)


class IContentType(interface.Interface):

    name = schema.TextLine(
        title = _(u'Name'),
        description = _(u'Content Type Name'),
        required = True)

    title = schema.TextLine(
        title = _(u'Title'),
        description = _(u'Content Type Title'),
        required = True)

    description = schema.Text(
        title = _(u'Description'),
        description = _(u'Content Type Description'),
        required = False)

    context = interface.Attribute('Context')
    specification = interface.Attribute('Schema')

    schemas = interface.Attribute('List of additional schemas')
    behaviors = interface.Attribute('List of additional behaviors')

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
