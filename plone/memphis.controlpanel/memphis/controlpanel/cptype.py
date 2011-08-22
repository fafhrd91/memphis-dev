""" control panel api """
import sys
from zope import interface
from zope.schema import getFields

from memphis import config
from memphis.controlpanel.configlet import Configlet


class ConfigletType(type):
    """ Metaclass for all configlets

    >>> from zope import interface, schema
    >>> from memphis.controlpanel import cptype

    >>> class IMyConfiglet(interface.Interface):
    ...   title = schema.TextLine(title = u'Title')

    >>> class MyConfiglet(object):
    ...   pass

    >>> ConfigletClass = ConfigletType(
    ...    'myconfiglet', IMyConfiglet, MyConfiglet, 'MyConfiglet', '')

    New class avilable by it's cname in
    memphis.content.controlpanel module

    >>> getattr(cptype, 'Configlet<myconfiglet>') is ConfigletClass
    True

    Automaticly generate schema fields to ConfigletProperty

    >>> ConfigletClass.title
    <memphis.controlpanel.cptype.ConfigletProperty object at ...>

    >>> configlet = ConfigletClass()
    >>> configlet
    <memphis.controlpanel.cptype.Configlet<myconfiglet> object at ...>

    >>> isinstance(configlet, MyConfiglet)
    True

    >>> isinstance(configlet, Configlet)
    True

    We also can use number of base classes

    >>> class MyConfiglet2(object):
    ...   pass

    >>> ConfigletClass = ConfigletType(
    ...    'myconfiglet', IMyConfiglet, MyConfiglet2, 'MyConfiglet', '')

    ConfigletClass without base class, so just for data

    >>> ConfigletClass = ConfigletType(
    ...    'myconfiglet2', IMyConfiglet, None, 'MyConfiglet2', '')

    >>> ConfigletClass
    <class 'memphis.controlpanel.cptype.Configlet<myconfiglet2>'>

    __schema__ attribute is immutable

    >>> configlet = ConfigletClass()

    >>> configlet.__schema__
    <InterfaceClass memphis.TESTS.IMyConfiglet>

    >>> configlet.__schema__ = IMyConfiglet
    Traceback (most recent call last):
    ...
    AttributeError: Can't set data property

    """

    def __new__(cls, name, schema, class_=None, *args, **kw):
        cname = 'Configlet<%s>'%name
        if class_ is not None:
            bases = (class_, Configlet)
        else:
            bases = (Configlet,)

        tp = type.__new__(cls, str(cname), bases, {})
        setattr(sys.modules['memphis.controlpanel.cptype'], cname, tp)

        return tp

    def __init__(cls, name, schema, class_=None, title='', description=''):
        for f_id in getFields(schema):
            if not hasattr(cls, f_id):
                setattr(cls, f_id, ConfigletProperty(schema[f_id]))

        cls.__id__ = DataProperty(name)
        cls.__title__ = DataProperty(title)
        cls.__description__ = DataProperty(description)
        cls.__schema__ = DataProperty(schema)


class DataProperty(object):

    def __init__(self, value):
        self.value = value

    def __get__(self, inst, klass):
        return self.value

    def __set__(self, inst, value):
        raise AttributeError("Can't set data property")


_marker = object()

class ConfigletProperty(object):
    """ Special property thats reads and writes values from
    instance's '__data__' attribute

    Let's define simple schema field

    >>> from zope import schema
    >>> field = schema.TextLine(
    ...    title = u'Test',
    ...    default = u'default value')
    >>> field.__name__ = 'attr1'

    Now we need content class

    >>> class Content(object):
    ...
    ...    attr1 = ConfigletProperty(field)

    Lets create class instance and add field values storage

    >>> ob = Content()
    >>> ob.__data__ = {}

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

    >>> ob.__data__['attr1']
    u'value1'

    If storage contains field value we shuld get it

    >>> ob.__data__['attr1'] = u'value2'
    >>> ob.attr1
    u'value2'

    We can't set value for readonly fields

    >>> field.readonly = True
    >>> ob.attr1 = u'value1'
    Traceback (most recent call last):
    ...
    ValueError: ('attr1', u'Field is readonly')

    >>> del ob.attr1
    >>> ob.__data__
    {}

    """

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self.__field = field
        self.__name = name

    def __get__(self, inst, klass):
        if inst is None:
            return self

        data = inst.__data__
        value = data.get(self.__name, _marker)
        if value is _marker:
            return self.__field.default

        return value

    def __set__(self, inst, value):
        data = inst.__data__

        field = self.__field.bind(inst)
        field.validate(value)
        if field.readonly and data.get(self.__name, _marker) is not _marker:
            raise ValueError(self.__name, u'Field is readonly')

        data[self.__name] = value

    def __delete__(self, inst):
        data = inst.__data__
        if self.__name in data:
            del data[self.__name]
