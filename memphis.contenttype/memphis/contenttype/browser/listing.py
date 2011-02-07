"""

$Id: listing.py 11771 2011-01-29 22:56:56Z fafhrd91 $
"""
from zope import interface
from memphis.contenttype.interfaces import IContentItem, IContentContainer


class ListingView(object):

    def update(self):
        container = IContentContainer(self.context)

        #base_url = self.request.resource_url()

        data = []

        for name, item in container.items():
            item = IContentItem(item, None)
            if item is None:
                continue

            info = {
                'name': item.__name__,
                'title': item.title,
                'description': item.description}

            data.append(item)

        self.data = data
