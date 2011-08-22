"""
behavior for factory
--------------------

  >>> from memphis import config, content
  >>> config.begin(packages=('memphis.content.meta',))

  >>> from zope import interface
  >>> from zope.component import getSiteManager
  >>> class Ob(object):
  ...     def __init__(self, iface):
  ...         interface.directlyProvides(self, iface)

  >>> class ITest(interface.Interface):
  ...     pass

  >>> class TestFactory(content.BehaviorFactoryBase):
  ...     content.behavior('test', ITest)

  >>> class TestFactory2(content.BehaviorFactoryBase):
  ...     pass
  ...
  >>> reGrok()

  >>> sm = getSiteManager()
  >>> print content.queryBehavior(ITest)
  None

  >>> config.commit()

  >>> bh = content.getBehavior(ITest)
  >>> isinstance(bh.factory, TestFactory)
  True

  >>> config.begin()
  >>> class TestFactory3(content.BehaviorFactoryBase):
  ...     content.behavior('test', ITest)

  >>> reGrok()
  >>> config.commit()
  Traceback (most recent call last):
  ...
  ConfigurationConflictError: Conflicting configuration actions
    ...

"""
import martian, sys
from zope import interface
from zope.interface.interface import InterfaceClass

from memphis import config
from memphis.content import registry, interfaces
from memphis.content.directives import schema, behavior
from memphis.content.registry import BehaviorBase, BehaviorFactoryBase


class SchemaGrokker(martian.InstanceGrokker):
    martian.component(InterfaceClass)
    martian.directive(schema)

    def grok(self, name, interface, configContext=config.UNSET, **kw):
        if interface in schemaExecuted and \
                not getattr(interface.__module__, '__fake_module__', False):
            return False
        schemaExecuted.append(interface)

        value = schema.bind(default=_marker).get(interface)
        if value is _marker:
            return False

        name, klass, type, t, d, info = value

        config.addAction(
            configContext,
            discriminator = ('memphis.content:schema', name),
            callable = registry.registerSchema,
            args = (name, interface, klass, type, t, d),
            order = (config.moduleNum(interface.__module__), 90),
            info = info)
        return True


class BehaviorGrokker(martian.ClassGrokker):
    martian.component(BehaviorBase)
    martian.directive(behavior)

    def execute(self, klass, configContext=None, **kw):
        value = behavior.bind(default=_marker).get(klass)
        if value is _marker:
            return False

        name, iface, schema, type, t, d, info = value

        if iface is None:
            provides = list(interface.implementedBy(klass))
            if len(provides) == 1:
                iface = provides[0]
            else:
                raise TypeError("Missing 'spec' attribute")

        config.addAction(
            configContext,
            discriminator = ('memphis.content:behavior', name),
            callable=registry.registerBehavior,
            args = (name, iface, klass, schema, type, t, d),
            order = (config.moduleNum(klass.__module__), 91),
            info = info)

        return True


class BehaviorFactoryGrokker(martian.ClassGrokker):
    martian.component(BehaviorFactoryBase)
    martian.directive(behavior)

    def execute(self, factory, configContext=None, **kw):
        value = behavior.bind(default=_marker).get(factory)
        if value is _marker:
            return False

        name, iface, schema, type, t, d, info = value

        config.addAction(
            configContext,
            discriminator = ('memphis.content:behavior', name),
            callable=registry.registerBehavior,
            args = (name, iface, factory(), schema, type, t, d),
            order = (config.moduleNum(factory.__module__), 91),
            info = info)

        return True


_marker = object()

schemaExecuted = []

@config.cleanup
def cleanUp():
    global schemaExecuted
    schemaExecuted[:] = []
