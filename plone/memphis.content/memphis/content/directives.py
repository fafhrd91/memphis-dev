from martian import Directive, CLASS, ONCE_NOBASE, ONCE_IFACE

from memphis import config
from memphis.config.directives import getInfo


class schema(Directive):
    scope = CLASS
    store = ONCE_IFACE

    def factory(self, name, klass=None, type=None, title=u'', description=u''):
        config.moduleNum(self.frame.f_locals['__module__'])
        return name, klass, type, title, description, getInfo()


class behavior(Directive):
    scope = CLASS
    store = ONCE_NOBASE

    def factory(self, name, iface=None, schema=None,
                type = None, title = u'', description = u''):
        config.moduleNum(self.frame.f_locals['__module__'])
        return name, iface, schema, type, title, description, getInfo()
