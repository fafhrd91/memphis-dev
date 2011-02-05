"""

$Id: api.py 11771 2011-01-29 22:56:56Z fafhrd91 $
"""
from zope.component import getSiteManager

from memphis import storage
from memphis.contenttype import behaviors
from memphis.contenttype.interfaces import \
    IContent, IContentItem, IContainer, IContentType, IContentTypeSchema
from memphis.contenttype.contenttype import \
    Content, ContentType, ContentTypeBehaviorFactory


def registerContentType(
    name, specification, klass=Content, behaviors=(), schemas=(),
    title='', description='', ct_factory=ContentType):
    """ Register new content type
    """

    sm = getSiteManager()

    # register new content behavior
    bh_name = 'content.type-%s'%name
    storage.registerBehavior(
        bh_name, specification, Content, '', None, title, description)

    behaviors = tuple(behaviors) + (bh_name,)
    ct = ct_factory(name, specification, behaviors, schemas, title, description)

    # register content type as named utility
    sm.registerUtility(ct, IContentType, name=name)

    return ct
