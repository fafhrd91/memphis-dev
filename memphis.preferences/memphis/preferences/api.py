"""

$Id: api.py 11800 2011-01-31 04:36:54Z fafhrd91 $
"""
from zope import interface
from zope.schema import getFields
from memphis import storage, config
from memphis.preferences import root, preference, preferencetype
from memphis.preferences.interfaces import IPreferences


def registerCategory(name, title, description='', configContext=None):
    def _register(category):
        root.Preferences.addCategory(category)

    category = preference.PreferenceCategory(name, title, description)

    config.addAction(
        configContext,
        discriminator= ('memphis.preferences:category', name),
        callable = _register, args = (category,))

    return category


def registerPreference(name, schema, klass=None,
                       title='', description='', configContext=None):
    if '.' in name:
        category, name = name.split('.', 1)
    else:
        category = ''

    PreferenceClass = preferencetype.PreferenceType(
        str(name), category, schema, klass, title, description)

    # register storage schema
    if getFields(schema):
        storage.registerSchema(
            'memphis.preferences-%s.%s'%(category, name), schema)

    # instance
    inst = PreferenceClass()

    # register preference in preferences
    def _register(preference):
        root.Preferences.addPreference(preference)

    config.addAction(
        configContext,
        discriminator = ('memphis.preferences:preference', category, name),
        callable = _register, args = (inst,))

    return inst
