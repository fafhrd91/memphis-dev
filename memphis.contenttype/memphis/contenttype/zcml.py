""" memphis:content directive

$Id: zcml.py 11771 2011-01-29 22:56:56Z fafhrd91 $
"""
from zope import component
from zope.schema import TextLine
from zope.component.zcml import utility

from zope import interface
from zope.configuration import fields

from memphis import storage

from memphis.contenttype.content import Content
from memphis.contenttype.interfaces import _
from memphis.contenttype.interfaces import IContentType
from memphis.contenttype.contenttype import ContentType


class IContentTypeDirective(interface.Interface):

    name = fields.PythonIdentifier(
        title = u'Name',
        description = u'Content name.',
        required = True)

    schema = fields.GlobalInterface(
        title = u'Schema',
        description = u'Content schema.',
        required = True)

    schemas = fields.Tokens(
        title = u'Schemas',
        description = u'Content type type.',
        required = False,
        value_type = TextLine())

    title = fields.MessageID(
        title = u'Title',
        description = u'Content title.',
        required = True)

    description = fields.MessageID(
        title = u'Description',
        description = u'Content description.',
        required = False)

    contenttype = fields.GlobalInterface(
        title = u'Content Type',
        description = u'Content type marker interface',
        required = False)

    ctclass = fields.GlobalObject(
        title = u'Content Type Class',
        description = u'Custom content type implementation',
        required = False)

    contains = fields.Tokens(
        title = u'Contains',
        description = u'Interface or content type name of contents '\
                            'that can be contained by this container.',
        required = False,
        value_type = TextLine())

    containers = fields.Tokens(
        title = u'Containers',
        description = u'Containers that can contain this type of content '\
                            u'(Content name or Interface).',
        required = False,
        value_type = TextLine())

    behaviors = fields.Tokens(
        title = u'Behaviors',
        description = u'List of behaviors',
        required = False,
        value_type = TextLine())


def contentHandler(_context, schema, name, title, schemas=(),
                   description='', contenttype=None, class_=None,
                   type=[], contains=(), containers=(), behaviors=()):

    # create content type
    if class_ is not None:
        if not IContentType.implementedBy(class_):
            raise ConfigurationError(
                'Custom content type implementation '\
                    'should implement IContentType interface.')
        ct_factory = class_
    else:
        ct_factory = ContentType

    bh_name = 'content.type-%s'%name
    storage.registerBehavior(
        bh_name, schema, Content, '', None, title, description)

    behaviors = tuple(behaviors) + (bh_name,)
    ct = ct_factory(name, schema, behaviors, schemas, title, description)

    # create named utility for content type
    utility(_context, IContentType, ct, name=name)
