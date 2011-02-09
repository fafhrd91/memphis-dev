"""
behavior for factory
--------------------

  >>> from memphis import config
  >>> config.begin(packages=('memphis.storage.meta',))

  >>> from zope import interface
  >>> from zope.component import getSiteManager
  >>> class Ob(object):
  ...     def __init__(self, iface):
  ...         interface.directlyProvides(self, iface)

  >>> class ITest(interface.Interface):
  ...     pass

  >>> class TestFactory(storage.BehaviorFactoryBase):
  ...     storage.behavior('test', ITest)

  >>> class TestFactory2(storage.BehaviorFactoryBase):
  ...     pass
  ...
  >>> reGrok()

  >>> sm = getSiteManager()
  >>> print storage.queryBehavior(ITest)
  None

  >>> config.commit()

  >>> bh = storage.getBehavior(ITest)
  >>> isinstance(bh.factory, TestFactory)
  True

  >>> config.begin()
  >>> class TestFactory3(storage.BehaviorFactoryBase):
  ...     storage.behavior('test', ITest)

  >>> reGrok()
  >>> config.commit()
  Traceback (most recent call last):
  ...
  ConfigurationConflictError: Conflicting configuration actions
    ...

"""
import martian
from zope import interface
from zope.interface.interface import InterfaceClass

from memphis import storage, config
from memphis.storage import registry, interfaces
from memphis.storage.directives import schema, relation, behavior

_marker = object()

schemaExecuted = []
relationExecuted = []


class SchemaGrokker(martian.InstanceGrokker):
    martian.component(InterfaceClass)
    martian.directive(schema)

    def grok(self, name, interface, configContext=None, **kw):
        if interface in schemaExecuted:
            return False
        schemaExecuted.append(interface)

        value = schema.bind(default=_marker).get(interface)
        if value is _marker:
            return False

        name, klass, type, t, d, info = value

        registry.registerSchema(
            name, interface, klass, type, t, d, configContext, info)
        return True


class RelationGrokker(martian.InstanceGrokker):
    martian.component(InterfaceClass)
    martian.directive(relation)

    martian.priority(99999999)

    def grok(self, name, interface, configContext=None, **kw):
        if interface in relationExecuted:
            return False
        relationExecuted.append(interface)

        value = relation.bind(default=_marker).get(interface)
        if value is _marker:
            return False

        name, klass, t, d, info = value

        registry.registerRelation(
            name, interface, klass, t, d, configContext, info)
        return True


class BehaviorGrokker(martian.ClassGrokker):
    martian.component(storage.BehaviorBase)
    martian.directive(behavior)

    def execute(self, klass, configContext=None, **kw):
        value = behavior.bind(default=_marker).get(klass)
        if value is _marker:
            return False

        name, iface, relation, schema, type, t, d, info = value

        if iface is None:
            iface = list(interface.implementedBy(klass))[0]

        registry.registerBehavior(
            name, iface, klass, relation, schema, type, t, d, configContext, info)
        return True


class BehaviorFactoryGrokker(martian.ClassGrokker):
    martian.component(storage.BehaviorFactoryBase)
    martian.directive(behavior)

    def execute(self, factory, configContext=None, **kw):
        value = behavior.bind(default=_marker).get(factory)
        if value is _marker:
            return False

        name, iface, relation, schema, type, t, d, info = value

        registry.registerBehavior(
            name, iface, factory(), 
            relation, schema, type, t, d, configContext, info)
        return True


@config.cleanup
def cleanUp():
    global schemaExecuted, relationExecuted
    schemaExecuted = []
    relationExecuted = []
