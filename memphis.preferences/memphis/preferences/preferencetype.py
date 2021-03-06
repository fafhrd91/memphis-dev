""" PreferenceGroup metaclass """
import sys
from zope import interface
from zope.schema import getFields
from memphis.preferences.interfaces import _
from memphis.preferences.preference import Preference

_marker = object()


class PreferenceType(type):
    """ Metaclass for all preference groups

    >>> from zope import interface, schema
    >>> from z3ext.preferences import preferencetype

    >>> class IMyPreference(interface.Interface):
    ...   title = schema.TextLine(title = u'Title')

    >>> class MyPreference(object):
    ...   pass

    >>> PreferenceClass = preferencetype.PreferenceType(
    ...    'mypreference', IMyPreference, MyPreference, 'MyPreference', '')

    New class avilable by it's cname in z3ext.preferences.preferencetype module

    >>> getattr(preferencetype, 'Preference<mypreference>') is PreferenceClass
    True

    Automaticly generate schema fields to PreferenceProperty

    >>> PreferenceClass.title
    <z3ext.preferences.preferencetype.PreferenceProperty object at ...>

    >>> preference = PreferenceClass()
    >>> preference
    <z3ext.preferences.preferencetype.Preference<mypreference> object at ...>

    >>> isinstance(preference, MyPreference)
    True

    >>> isinstance(preference, preferencetype.PreferenceGroup)
    True

    We also can use number of base classes

    >>> class MyPreference2(object):
    ...   pass

    >>> PreferenceClass = preferencetype.PreferenceType(
    ...    'mypreference', IMyPreference,
    ...    (MyPreference, MyPreference2), 'MyPreference', '')

    """

    def __new__(cls, name, category, schema, class_=None, *args, **kw):
        cname = 'Preference<%s>'%name
        if type(class_) is tuple:
            bases = class_ + (Preference,)
        elif class_ is not None:
            bases = (class_, Preference)
        else:
            bases = (Preference,)

        tp = type.__new__(cls, str(cname), bases, {})
        setattr(sys.modules['memphis.preferences.preferencetype'], cname, tp)

        return tp

    def __init__(cls, name, category, schema,
                 class_=None, title='', description=''):
        for f_id in getFields(schema):
            if not hasattr(cls, f_id):
                setattr(cls, f_id, PreferenceProperty(schema[f_id]))

        interface.classImplements(cls, schema)

        cls.__id__ = name
        cls.__category__ = category
        cls.__title__ = title
        cls.__description__ = description
        cls.__schema__ = DataProperty(schema)
        interface.classImplements(cls, schema)


class DataProperty(object):

    def __init__(self, schema):
        self.schema = schema

    def __get__(self, inst, klass):
        return self.schema

    def __set__(self, inst, value):
        raise AttributeError("Can't change __schema__")


class PreferenceProperty(object):
    """ Special property thats reads and writes values from
    instance's 'data' attribute

    Let's define simple schema field

    >>> from zope import schema
    >>> field = schema.TextLine(
    ...    title = u'Test',
    ...    default = u'default value')
    >>> field.__name__ = 'attr1'

    >>> from z3ext.preferences.storage import DataStorage

    Now we need content class

    >>> from z3ext.preferences.preferencetype import PreferenceProperty
    >>> class Content(object):
    ...
    ...    attr1 = PreferenceProperty(field)

    Lets create class instance and add field values storage

    >>> ob = Content()
    >>> ob.data = DataStorage({}, None)

    By default we should get field default value

    >>> ob.attr1
    u'default value'

    We can set only valid value

    >>> ob.attr1 = 'value1'
    Traceback (most recent call last):
    ...
    WrongType: ('value1', <type 'unicode'>, 'attr1')

    >>> ob.attr1 = u'value1'
    >>> ob.attr1
    u'value1'

    If storage contains field value we shuld get it

    >>> ob.data.attr1 = u'value2'
    >>> ob.attr1
    u'value2'

    We can't set value for readonly fields

    >>> field.readonly = True
    >>> ob.attr1 = u'value1'
    Traceback (most recent call last):
    ...
    ValueError: ('attr1', u'Field is readonly')

    Remove attribute

    >>> del ob.attr1

    """

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self._field = field
        self._name = name

    def __get__(self, inst, klass):
        if inst is None:
            return self

        datasheet = inst.__data__
        value = getattr(datasheet, self._name, _marker)
        if value is _marker:
            return self._field.default

        return value

    def __set__(self, inst, value):
        datasheet = inst.__data__

        field = self._field.bind(inst)
        field.validate(value)
        if field.readonly and \
                getattr(datasheet, self._name, _marker) is not _marker:
            raise ValueError(self._name, _(u'Field is readonly'))

        setattr(datasheet, self._name, value)

    def __delete__(self, inst):
        datasheet = inst.__data__
        if hasattr(datasheet, self._name):
            delattr(datasheet, self._name)
