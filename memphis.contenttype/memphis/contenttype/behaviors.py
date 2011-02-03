"""

$Id: behaviors.py 11771 2011-01-29 22:56:56Z fafhrd91 $
"""
from zope import interface
from memphis import storage
from interfaces import IContentItem


class ContentItem(object):
    interface.implements(IContentItem)
    #storage.behavior('content.item',
    #                 relation = 'base.container',
    #                 title = 'Content item',
    #                 description = 'Base behavior for content items.')

    def __init__(self, item, relation):
        super(ContentItem, self).__init__(item, relation)
        self.data = item.getDatasheet(IContentItem)

    @property
    def title(self):
        return self.data.title or u'No title'

    @property
    def description(self):
        return self.data.description
