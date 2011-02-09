import pyramid.url
from zope.schema import getFieldsInOrder
from zope.component import getUtilitiesFor
from memphis import form, config, container, view, storage, ttwschema
from memphis.contenttype.interfaces import _, IContentTypeSchema
from memphis.contenttype.interfaces import ISchemaType, IBehaviorType


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

    fields = form.Fields(IContentTypeSchema).omit(
        'schemas', 'schemaFields', 'behaviors', 'behaviorActions')

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

    def listFields(self, sch):
        return [field for n, field in getFieldsInOrder(sch.specification)]

    def update(self):
        context = self.context
        request = self.request

        if 'form-addschema' in request.params:
            view.addStatusMessage(
                request, 'Content type schemas have been modified.')

            context.schemas = context.schemas + tuple(
                request.params.getall('schema-id'))

        elif 'form-remove' in request.params:
            view.addStatusMessage(
                request, 'Content type schemas have been modified.')
            
            rem_sch = request.params.getall('schema-id')
            context.schemas = tuple(
                [sch for sch in context.schemas if sch not in rem_sch])

        schemas = {}

        for name, schema in getUtilitiesFor(ISchemaType):
            schemas[name] = (schema.title, schema)

        for name, schema in getUtilitiesFor(ttwschema.ISchemaType):
            schemas[name] = (schema.title, schema)

        enabled = []
        if 'content.item' not in context.schemas:
            context.schemas = context.schemas + ('content.item',)

        for schId in self.context.schemas:
            if schId in schemas:
                enabled.append(schemas[schId][1])
        
        self.enabled = enabled

        schemas = schemas.values()
        schemas.sort()
        self.schemas = [schema for t, schema in schemas 
                        if schema.name not in self.context.schemas]


class ContentTypeBehaviors(view.View):
    view.pyramidView(
        'behaviors.html', IContentTypeSchema,
        template = view.template('memphis.contenttype:templates/behaviors.pt'))

    def update(self):
        behaviors = []

        for name, bh in getUtilitiesFor(IBehaviorType):
            behaviors.append((bh.title, bh))

        behaviors.sort()
        self.behaviors = [behavior for t, behavior in behaviors]

        request = self.request
        if 'form-save' in request.params:
            view.addStatusMessage(
                request, 'Content type behaviors have been modified.')

            self.context.behaviors = request.params.getall('form-behaviors')
