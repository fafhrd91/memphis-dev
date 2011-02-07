import pyramid.url
from zope.component import getUtility
from memphis import form, config, container, view, storage, ttwschema

from memphis.contenttype.interfaces import _, IContentType


class AddContent(container.AddContentForm, view.View):
    view.pyramidView('', IContentType)

    @property
    def fields(self):
        schemas = []
        for schId in self.context.schemas:
            schemas.append(getUtility(storage.ISchema, schId).specification)

        return form.Fields(schemas[0])

    def update(self):
        super(AddContent, self).update()
