from zope.component import getSiteManager
from zope.interface.adapter import AdapterRegistry
from zope.interface.interface import InterfaceClass

from memphis import config
from memphis.storage import hooks
from memphis.storage.schema import Schema
from memphis.storage.behavior import Behavior, BehaviorBase
from memphis.storage.interfaces import ISchema, IBehavior
from memphis.storage.exceptions import BehaviorNotFound, SchemaNotFound


class Registry(object):

    def __init__(self):
        self.behaviors = AdapterRegistry()
        self.behaviornames = {}
        self.schemas = AdapterRegistry()
        self.schemanames = {}
        self.relations = {}

    def getRelation(self, key):
        return self.relations[key]

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

    def registerRelation(self, rel, schema):
        self.relations[schema] = rel

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

def getRelation(name):
    return registry.getRelation(name)

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
                   title='', description='', configContext=None, info=''):

    def _register(name, schema, klass, type, title, description):
        sob = Schema(name, schema, klass, title, description)

        for tp in type:
            getSiteManager().registerUtility(sob, tp, name)

        # register in internal registry
        registry.registerSchema(sob)

        session = hooks.getSession()
        if session is not None:
            hooks.getMetadata().create_all()
            session.flush()

    if type is None:
        type = (ISchema,)
    elif isinstance(type, InterfaceClass):
        type = (type,)

    config.addAction(
        configContext,
        discriminator = ('memphis.storage:schema', name),
        callable=_register, args=(name,schema,klass,type,title, description),
        info = info)


def registerRelation(name, schema, klass=None,
                     title='', description='', configContext=None, info=''):
    # fixme: remove this line
    from memphis.storage.relation import Relation, buildRelation

    def _register(name, schema, klass, title, description):
        if klass is not None:
            rel = Relation(name, klass, title, description)
        else:
            rel = buildRelation(name, schema, title, description)

        registry.registerRelation(rel, schema)

        # create table
        session = hooks.getSession()
        if session is not None:
            hooks.getMetadata().create_all()
            session.flush()

    config.addAction(
        configContext,
        discriminator = ('memphis.storage:relation', name),
        callable=_register, args=(name, schema, klass, title, description),
        info = info)


def registerBehavior(name, spec, factory, relation=None, schema=None,
                     type = None, title='', description = '', 
                     configContext=None, info=''):

    def _register(name, spec, factory, relation, schema, type, title,description):
        # check relation
        if relation:
            getRelation(relation)

        bh = Behavior(name, title, spec, relation, factory, schema, description)

        for tp in type:
            getSiteManager().registerUtility(bh, tp, name)

        # register in internal registry
        registry.registerBehavior(bh)

    if type is None:
        type = (IBehavior,)
    elif isinstance(type, InterfaceClass):
        type = (type,)

    config.addAction(
        configContext,
        ('memphis.storage:registerBehavior', name),
        callable= _register,
        args=(name, spec, factory, relation, schema, type, title, description),
        info=info)


@config.cleanup
def cleanUp():
    global registry
    registry = Registry()
