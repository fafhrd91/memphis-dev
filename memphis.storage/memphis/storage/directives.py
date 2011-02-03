"""

$Id: directives.py 11770 2011-01-29 22:55:31Z fafhrd91 $
"""
from martian import Directive, CLASS, ONCE_NOBASE, ONCE_IFACE

from memphis.config.directives import getInfo


class schema(Directive):
    scope = CLASS
    store = ONCE_IFACE

    def factory(self, name, klass=None, title = u'', description = u''):
        return name, klass, title, description, getInfo()


class relation(Directive):
    scope = CLASS
    store = ONCE_IFACE

    def factory(self, name, klass=None, title = u'', description = u''):
        return name, klass, title, description, getInfo()


class behavior(Directive):
    scope = CLASS
    store = ONCE_NOBASE

    def factory(self, name, iface=None, relation=None, schema=None,
                title = u'', description = u''):
        return name, iface, relation, schema, title, description, getInfo()
