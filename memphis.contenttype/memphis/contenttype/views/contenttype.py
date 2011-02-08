import pyramid.url
from zope import interface
from zope.component import getUtility, queryUtility
from memphis import form, config, container, view, storage, ttwschema

from memphis.contenttype.interfaces import _, IContent, IContentType


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


class EditContent(form.Form, view.View):
    view.pyramidView('edit.html', IContent)

    @property
    def fields(self):
        print list(interface.providedBy(self.context))
        ct = IContentType(self.context)
        print '===========', ct
        print '-----------', self.context.schemas

        schemas = []
        for schId in self.context.schemas:
            schema = queryUtility(storage.ISchema, schId)
            if schema is not None:
                schemas.append(schema.specification)

        return form.Fields(schemas[0])
