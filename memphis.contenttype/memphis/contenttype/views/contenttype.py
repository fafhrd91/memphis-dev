import pyramid.url
from zope import interface
from zope.component import getSiteManager, queryUtility, getUtilitiesFor
from memphis import form, config, view, storage
from memphisttw import schema
from memphis.contenttype.interfaces import _
from memphis.contenttype.interfaces import ISchemaType, IBehaviorType
from memphis.contenttype.interfaces import IContent, IContentTypeSchema


config.action(
    view.registerDefaultView,
    'index.html', IContentTypeSchema)

config.action(
    view.registerActions,
    ('index.html', IContentTypeSchema, 
     _('View'), _('View content type'), 10),
    ('edit.html', IContentTypeSchema, 
     _('Edit'), _('Edit content type'), 20),
    ('schemas.html', IContentTypeSchema, 
     _('Schemas'), _('Content type schemas'), 30),
    ('behaviors.html', IContentTypeSchema, 
     _('Behaviors'), _('Content type behaviors'), 40),
    ('actions.html', IContentTypeSchema, 
     _('Actions'), _('Content type actions'), 50))


class ContentTypeView(view.View):
    view.pyramidView(
        'index.html', IContentTypeSchema,
        template = view.template(
            'memphis.contenttype:templates/contenttype.pt'))

    def update(self):
        schemas = []
        for sId in self.context.schemas:
            sch = queryUtility(storage.ISchema, sId)
            if sch is not None:
                schemas.append(sch)

        self.schemas = schemas

        behaviors = []
        for bId in self.context.behaviors:
            bh = queryUtility(IBehaviorType, bId)
            if bh is not None:
                behaviors.append(bh)
        self.behaviors = behaviors


class ContentTypeEdit(form.EditForm, view.View):
    view.pyramidView('edit.html', IContentTypeSchema)

    fields = form.Fields(IContentTypeSchema).omit(
        'schemas', 'hiddenFields', 'behaviors', 'behaviorActions', 'widgets')

    @property
    def label(self):
        return self.context.title

    @property
    def description(self):
        return self.context.description


class ContentTypeSchemas(form.Form, view.View):
    view.pyramidView(
        'schemas.html', IContentTypeSchema,
        template = view.template('memphis.contenttype:templates/schemas.pt'))

    def listFields(self, sch):
        return [field for n, field in schema.getFieldsInOrder(sch.spec)]

    def getDefault(self, schId, fldId):
        if self.context.widgets:
            widgets = self.context.widgets
            return widgets.get(schId, {}).get(fldId, None)
        return None

    def getWidgets(self, field):
        widgets = []
        default = None
        for name, widget in self.adapters.lookupAll(
            (interface.providedBy(field), self.requestProvided), form.IWidget):
            if not name:
                default = widget
            else:
                widgets.append(widget)
        return default, widgets

    def update(self):
        super(ContentTypeSchemas, self).update()

        self.adapters = getSiteManager().adapters
        self.requestProvided = interface.providedBy(self.request)

        context = self.context
        request = self.request

        if 'form-addschema' in request.params:
            view.addMessage(
                request, 'Content type schemas have been modified.')

            context.schemas = context.schemas + tuple([
                    id for id in request.params.getall('schema-id')
                    if id not in context.schemas])

        schemas = {}

        for name, sch in getUtilitiesFor(ISchemaType):
            schemas[name] = (sch.title, sch)

        for name, sch in getUtilitiesFor(schema.ISchemaType):
            schemas[name] = (sch.title, sch)

        enabled = []
        for schId in self.context.schemas:
            if schId in schemas:
                enabled.append(schemas[schId][1])
        
        self.enabled = enabled

        schemas = schemas.values()
        schemas.sort()
        self.schemas = [sch for t, sch in schemas 
                        if sch.name not in self.context.schemas]

        fields = []
        for sch, data in self.context.hiddenFields.items():
            for fid in data:
                fields.append('%s:%s'%(sch, fid))

        self.fields = fields

    @form.buttonAndHandler(u'Remove')
    def removeHandler(self, action):
        rem_sch = self.request.params.getall('schema-id')
        self.context.schemas = tuple(
            [sch for sch in self.context.schemas if sch not in rem_sch])

        view.addMessage(self.request,'Content type schemas have been modified.')

    @form.buttonAndHandler(u'Modify hidden')
    def modifyHandler(self, action):
        ids = self.request.params.getall('field-id')

        hidden = {}
        for fid in ids:
            sch, field = fid.split(':', 1)
            hidden.setdefault(sch, []).append(field)

        self.context.hiddenFields = hidden

        view.addMessage(self.request, 'Hidden fields have been modified.')

    @form.buttonAndHandler(u'Modify widgets')
    def modifyHandler(self, action):
        data = {}
        for key, val in self.request.params.items():
            if key.startswith('field:') and val != '__sys_default__':
                schName, fldId = key[6:].split(':', 1)
                data.setdefault(schName, {})[fldId] = val

        if data != self.context.widgets:
            self.context.widgets = data
            view.addMessage(self.request, 'Widgets have been modified.')

    def changeOrder(self, names, up=True):
        schemas = list(self.context.schemas)
        schemas_len = len(schemas)

        for name in names:
            idx = schemas.index(name)
            if up:
                new = idx - 1
                if new < 0 or schemas[new] in names:
                    continue
            else:
                new = idx + 1
                if new >= schemas_len or schemas[new] in names:
                    continue

            del schemas[idx]
            schemas.insert(new, name)

        self.context.schemas = tuple(schemas)
        view.addMessage(self.request, 'Schemas order has been changed.')

    @form.buttonAndHandler(u'Move up')
    def upHandler(self, action):
        self.changeOrder(self.request.params.getall('schema-id'), True)

    @form.buttonAndHandler(u'Move down')
    def downHandler(self, action):
        self.changeOrder(self.request.params.getall('schema-id'), False)


class ContentTypeBehaviors(form.Form, view.View):
    view.pyramidView(
        'behaviors.html', IContentTypeSchema,
        template = view.template('memphis.contenttype:templates/behaviors.pt'))

    def update(self):
        super(ContentTypeBehaviors, self).update()

        behaviors = [(bh.title, bh)
                     for name, bh in getUtilitiesFor(IBehaviorType)]
        behaviors.sort()
        self.behaviors = [storage.getBehavior(IContent)] + \
            [behavior for t, behavior in behaviors]

    @form.buttonAndHandler(u'Save')
    def saveHandler(self, action):
        self.context.behaviors = self.request.params.getall('behavior-id')

        view.addMessage(
            self.request, 'Content type behaviors have been modified.')


class ContentTypeActions(form.Form, view.View):
    view.pyramidView(
        'actions.html', IContentTypeSchema,
        template = view.template('memphis.contenttype:templates/bhactions.pt'))

    def update(self):
        super(ContentTypeActions, self).update()

        self.adapters = adapters = getSiteManager().adapters

        actions = []
        for bh in ('content.item',) + tuple(self.context.behaviors):
            behavior = storage.queryBehavior(bh)
            if behavior is None:
                behavior = queryUtility(IBehaviorType, bh)
                
            if behavior is not None:
                for name, action in adapters.lookupAll(
                    (behavior.spec,), view.IAction):
                    actions.append((action, behavior))

        self.behaviorActions = actions

    @form.buttonAndHandler(u'Hide')
    def modifyHandler(self, action):
        ids = self.request.params.getall('field-id')

        hidden = {}
        for fid in ids:
            sch, field = fid.split(':', 1)
            hidden.setdefault(sch, []).append(field)

        self.context.hiddenFields = hidden

        view.addMessage(self.request, 'Hidden fields have been modified.')

    def changeOrder(self, names, up=True):
        schemas = list(self.context.schemas)
        schemas_len = len(schemas)

        for name in names:
            idx = schemas.index(name)
            if up:
                new = idx - 1
                if new < 0 or schemas[new] in names:
                    continue
            else:
                new = idx + 1
                if new >= schemas_len or schemas[new] in names:
                    continue

            del schemas[idx]
            schemas.insert(new, name)

        self.context.schemas = tuple(schemas)
        view.addMessage(self.request, 'Schemas order has been changed.')

    @form.buttonAndHandler(u'Move up')
    def upHandler(self, action):
        self.changeOrder(self.request.params.getall('schema-id'), True)

    @form.buttonAndHandler(u'Move down')
    def downHandler(self, action):
        self.changeOrder(self.request.params.getall('schema-id'), False)
