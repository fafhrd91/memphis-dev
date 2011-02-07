import pyramid.url
from zope.component import getUtilitiesFor
from memphis import form, config, container, view, storage, ttwschema
from memphis.contenttype.interfaces import _, ISchemaType, IContentTypeSchema


config.action(
    view.registerDefaultView,
    'index.html', IContentTypeSchema)


class CTViewAction(container.Action):
    config.adapts(IContentTypeSchema, 'view')

    name = 'index.html'
    title = _('View')
    description = _('View content type')


class CTEditAction(container.Action):
    config.adapts(IContentTypeSchema, 'edit')

    name = 'edit.html'
    title = _('Edit')
    description = _('Edit content type')


class CTSchemasAction(container.Action):
    config.adapts(IContentTypeSchema, 'schemas')

    name = 'schemas.html'
    title = _('Schemas')
    description = _('Content type schemas')


class CTBehaviorsAction(container.Action):
    config.adapts(IContentTypeSchema, 'behaviors')

    name = 'behaviors.html'
    title = _('Behaviors')
    description = _('Content type behaviors')


class ContentTypeView(view.View):
    view.pyramidView(
        'index.html', IContentTypeSchema,
        template = view.template(
            'memphis.contenttype:templates/contenttype.pt'))


class ContentTypeEdit(form.EditForm, view.View):
    view.pyramidView('edit.html', IContentTypeSchema)

    fields = form.Fields(IContentTypeSchema).omit('schemas', 'behaviors')

    @property
    def label(self):
        return self.context.title

    @property
    def description(self):
        return self.context.description


class ContentTypeSchemas(view.View):
    view.pyramidView(
        'schemas.html', IContentTypeSchema,
        template = view.template('memphis.contenttype:templates/schemas.pt'))

    def update(self):
        schemas = {}
        
        for name, schema in getUtilitiesFor(ISchemaType):
            schemas[name] = (schema.title, schema)

        for name, schema in getUtilitiesFor(ttwschema.ISchemaType):
            schemas[name] = (schema.title, schema)
        
        schemas = schemas.values()
        schemas.sort()
        self.schemas = [schema for t, schema in schemas]

        request = self.request
        if 'form-save' in request.params:
            view.addStatusMessage(
                request, 'Content type schemas have been modified.')

            self.context.schemas = request.params.getall('form-schemas')


class ContentTypeBehaviors(view.View):
    view.pyramidView(
        'behaviors.html', IContentTypeSchema,
        template = view.template('memphis.contenttype:templates/behaviors.pt'))

    def update(self):
        schemas = storage.getSchema(ttwschema.ISchema)
        for schema in schemas.query():
            print schema
