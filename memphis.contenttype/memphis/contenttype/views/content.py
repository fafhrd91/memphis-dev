import pyramid.url
from zope import interface
from zope.component import getUtility, queryUtility
from memphis import form, config, container, view, storage, ttwschema

from memphis.contenttype.interfaces import _, IContent, IContentType


class AddContent(container.AddContentForm, view.View):
    view.pyramidView('', IContentType)

    fields = form.Fields()

    def update(self):
        ct = IContentType(self.context)
        print '===========', ct
        print '-----------', self.context.schemas

        forms = []
        for schId in ('content.item',) + tuple(self.context.schemas):
            schema = queryUtility(storage.ISchema, schId)
            if schema is not None:
                form = EditDatasheet(schema.Type(), self.request, self)
                form.update()
                forms.append(form)

        self.subforms = forms

        super(AddContent, self).update()
        
    #@property
    #def fields(self):
    #    schemas = []
    #    for schId in self.context.schemas:
    #        schemas.append(getUtility(storage.ISchema, schId).specification)

    #    return form.Fields(schemas[0])

    #def update(self):
    #    super(AddContent, self).update()


class EditDatasheet(form.EditSubForm):

    @property
    def fields(self):
        return form.Fields(self.context.__schema__)

    @property
    def label(self):
        return self.context.__title__

    @property
    def description(self):
        return self.context.__description__


class EditContent(form.EditForm, view.View):
    view.pyramidView('edit.html', IContent)

    fields = form.Fields()

    def update(self):
        ct = IContentType(self.context)
        print '===========', ct
        print '-----------', self.context.schemas

        forms = []
        for schId in self.context.schemas:
            schema = queryUtility(storage.ISchema, schId)
            if schema is not None:
                form = EditDatasheet(schema.Type(), self.request)
                form.update()
                forms.append(form)

        self.subforms = forms
