from zope import interface
from zope.component import getSiteManager
from zope.interface.adapter import AdapterRegistry
from zope.interface.interface import InterfaceClass

from memphis import config
from memphis.content.datasheet import DatasheetType
from memphis.content.interfaces import ISchema, IBehavior, IBehaviorBase
from memphis.content.exceptions import BehaviorNotFound, SchemaNotFound


class BehaviorBase(object):

    __behavior__ = None

    def __init__(self, context):
        self.__context__ = context


class BehaviorFactoryBase(object):
    pass


class Behavior(object):
    interface.implements(IBehavior)

    def __init__(self, name, title, spec, factory, schema=None, description=''):
        self.name = name
        self.title = title
        self.description = description
        self.spec = spec
        self.schema = schema
        self.factory = factory

        if type(factory) is type and issubclass(factory, BehaviorBase):
            factory.__behavior__ = self

    def __call__(self, instance):
        return self.factory(instance)


class Schema(object):
    interface.implements(ISchema)

    def __init__(self, name, schema, klass, title, description):
        self.name = name
        self.title = title
        self.description = description
        self.spec = schema

        if klass is not None:
            self.Type = klass
        else:
            self.Type = DatasheetType(
                self.name, schema, 
                title=self.title, description=self.description)

    def __call__(self, instance=None):
        return self.Type(instance)


class Registry(object):

    def __init__(self):
        self.behaviors = AdapterRegistry()
        self.behaviornames = {}
        self.schemas = AdapterRegistry()
        self.schemanames = {}

    def querySchema(self, schema, default=None):
        if isinstance(schema, basestring):
            return self.schemanames.get(schema, default)

        return self.schemas.lookup((ISchema,), schema, default=default)

    def queryBehavior(self, provided, spec, default=None):
        if isinstance(provided, basestring):
            return self.behaviornames.get(provided, default)

        if isinstance(provided, InterfaceClass):
            provided = (provided,)

        return self.behaviors.lookup(provided, spec, default=default)

    def registerSchema(self, schema):
        self.schemas.register((ISchema,), schema.spec, '', schema)
        self.schemanames[schema.name] = schema

    def registerBehavior(self, behavior):
        self.behaviors.register((behavior.spec,), IBehavior, '', behavior)
        self.behaviors.register((behavior.spec,), behavior.spec, '', behavior)
        self.behaviornames[behavior.name] = behavior


registry = Registry()


def getSchema(schema):
    inst = querySchema(schema)
    if inst is None:
        raise SchemaNotFound(schema)
    return inst


def getBehavior(provided, spec=None):
    bh = queryBehavior(provided, spec)
    if bh is None:
        raise BehaviorNotFound((provided, spec))

    return bh


def querySchema(sch):
    return registry.querySchema(sch)


def queryBehavior(provided, spec=None, default=None):
    if spec is None:
        spec = IBehavior
    return registry.queryBehavior(provided, spec)


def registerSchema(name, schema, klass=None, type=None,
                   title='', description='', 
                   configContext=config.UNSET, info=''):

    usedName = schema.queryTaggedValue('__sch_name__')
    if usedName and usedName != name:
        raise TypeError(
            "Can't use same interface for different schemas (%s and %s)."%(
                name, schema.getTaggedValue('__sch_name__')))

    schema.setTaggedValue('__sch_name__', name)

    if type is None:
        type = (ISchema,)
    elif isinstance(type, InterfaceClass):
        type = (type,)

    sob = Schema(name, schema, klass, title, description)

    for tp in type:
        getSiteManager().registerUtility(sob, tp, name)

    # register in internal registry
    registry.registerSchema(sob)


def registerBehavior(name, spec, factory, schema=None,
                     type = None, title='', description = '', 
                     configContext=None, info=''):

    usedName = spec.queryTaggedValue('__bh_name__')
    if usedName and usedName != name:
        raise TypeError(
            "Can't use same interface for different behaviors (%s and %s)."%(
                name, spec.getTaggedValue('__bh_name__')))
    elif spec.queryTaggedValue('__sch_name__'):
        raise TypeError(
            "Can't use same interface for schema and behavior (%s and %s)."%(
                name, spec.getTaggedValue('__sch_name__')))

    spec.setTaggedValue('__bh_name__', name)
    if schema is not None:
        spec.setTaggedValue('__bh_schema__', schema)

    if type is None:
        type = (IBehavior,)
    elif isinstance(type, InterfaceClass):
        type = (type,)

    bh = Behavior(name, title, spec, factory, schema, description)

    for tp in type:
        getSiteManager().registerUtility(bh, tp, name)

    # register in internal registry
    registry.registerBehavior(bh)


@config.cleanup
def cleanUp():
    global registry
    registry = Registry()
