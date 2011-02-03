"""

$Id: actions.py 11728 2011-01-26 22:39:30Z fafhrd91 $
"""
from webob.exc import HTTPFound

from zope.component import getUtility, getUtilitiesFor
#from memphis.form import Fields, PageletAddForm, PageletEditForm
from memphis.storage.interfaces import ISchema
from memphis.contenttype.interfaces import IContentType


class AddView(object):

    def update(self):
        data = []
        for name, ct in getUtilitiesFor(IContentType):
            data.append(
                {'name': name,
                 'title': ct.title,
                 'description': 'Behaviors: ' + str(ct.behaviors),
                 }
                )

        self.data = data


class AddContent: #(PageletAddForm):

    def __init__(self, context, request):
        super(AddContent, self).__init__(context, request)

        self.ctname = request.params['ctname']
        self.ct = getUtility(IContentType, self.ctname)
        self.hiddenValues = {'ctname': self.ctname}

    def getContent(self):
        return {}

    def createAndAdd(self, data):
        bct = self.ct.__bind__(self.context)

        item = bct.create()

        print list(item.schemas)

        ds = item.getDatasheet('content.type-%s'%self.ctname)
        for key, val in data.items():
            setattr(ds, key, val)

        bct.add(item)
        self.redirect()
        return HTTPFound(location='./listing.html')

    #def update(self):
    #    sch = getUtility(ISchema, self.ctname)
    #    self.data =

    @property
    def fields(self):
        return Fields(self.ct.schema)

    @property
    def label(self):
        return self.ct.title

    @property
    def description(self):
        return self.ct.description
