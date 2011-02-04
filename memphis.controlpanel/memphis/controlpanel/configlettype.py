""" Configlet metaclass

$Id: configlettype.py 11787 2011-01-31 00:38:52Z fafhrd91 $
"""
import sys
from zope.schema import getFields

from memphis.controlpanel.interfaces import _
from memphis.controlpanel.configlet import Configlet


_marker = object()


class ConfigletType(type):
    """ Metaclass for all configlets

    >>> from zope import interface, schema
    >>> from memphis.controlpanel import configlettype

    >>> class IMyConfiglet(interface.Interface):
    ...   title = schema.TextLine(title = u'Title')

    >>> class MyConfiglet(object):
    ...   pass

    >>> ConfigletClass = configlettype.ConfigletType(
    ...    'myconfiglet', IMyConfiglet, MyConfiglet, 'MyConfiglet', '')

    New class avilable by it's cname in
    memphis.controlpanel.configlettype module

    >>> getattr(configlettype, 'Configlet<myconfiglet>') is ConfigletClass
    True

    Automaticly generate schema fields to ConfigletProperty

    >>> ConfigletClass.title
    <memphis.controlpanel.configlettype.ConfigletProperty object at ...>

    >>> configlet = ConfigletClass()
    >>> configlet
    <memphis.controlpanel.configlettype.Configlet<myconfiglet> object at ...>

    >>> isinstance(configlet, MyConfiglet)
    True

    >>> isinstance(configlet, configlettype.Configlet)
    True

    We also can use number of base classes

    >>> class MyConfiglet2(object):
    ...   pass

    >>> ConfigletClass = configlettype.ConfigletType(
    ...    'myconfiglet', IMyConfiglet,
    ...    (MyConfiglet, MyConfiglet2), 'MyConfiglet', '')

    ConfigletClass without base class, so just for data

    >>> ConfigletClass = configlettype.ConfigletType(
    ...    'myconfiglet2', IMyConfiglet, None, 'MyConfiglet2', '')

    >>> ConfigletClass
    <class 'memphis.controlpanel.configlettype.Configlet<myconfiglet2>'>

    __schema__ attribute is immutable

    >>> configlet = ConfigletClass()

    >>> configlet.__schema__
    <InterfaceClass memphis.controlpanel.configlettype.IMyConfiglet>

    >>> configlet.__schema__ = IMyConfiglet
    Traceback (most recent call last):
    ...
    AttributeError: Can't set __schema__

    """

    def __new__(cls, name, schema, class_=None, *args, **kw):
        cname = 'Configlet<%s>'%name
        if type(class_) is tuple:
            bases = class_ + (Configlet,)
        elif class_ is not None:
            bases = (class_, Configlet)
        else:
            bases = (Configlet,)

        tp = type.__new__(cls, str(cname), bases, {})
        setattr(sys.modules['memphis.controlpanel.configlettype'], cname, tp)

        return tp

    def __init__(cls, name, schema, class_=None, title='', description=''):
        for f_id in getFields(schema):
            if not hasattr(cls, f_id):
                setattr(cls, f_id, ConfigletProperty(schema[f_id]))

        cls.__id__ = name
        cls.__bid__ = 'memphis.controlpanel-%s'%name
        cls.__title__ = title
        cls.__description__ = description
        cls.__schema__ = DataProperty(schema)


class DataProperty(object):

    def __init__(self, schema):
        self.schema = schema

    def __get__(self, inst, klass):
        return self.schema

    def __set__(self, inst, value):
        raise AttributeError("Can't set __schema__")


class ConfigletProperty(object):
    """ Special property thats reads and writes values from
    instance's 'data' attribute

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

    >>> class Datasheet(object):
    ...     def __init__(self):
    ...         self.data = {}

    Lets create class instance and add field values storage

    >>> ob = Content()
    >>> ob.datasheet = Datasheet()

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

    >>> ob.datasheet.data['attr1']
    u'value1'

    If storage contains field value we shuld get it

    >>> ob.datasheet.data['attr1'] = u'value2'
    >>> ob.attr1
    u'value2'

    We can't set value for readonly fields

    >>> field.readonly = True
    >>> ob.attr1 = u'value1'
    Traceback (most recent call last):
    ...
    ValueError: ('attr1', u'Field is readonly')

    >>> del ob.attr1
    >>> ob.datasheet.data
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

        datasheet = inst.datasheet
        value = datasheet.data.get(self.__name, _marker)
        if value is _marker:
            return self.__field.default

        return value

    def __set__(self, inst, value):
        datasheet = inst.datasheet

        field = self.__field.bind(inst)
        field.validate(value)
        if field.readonly and \
               datasheet.data.get(self.__name, _marker) is not _marker:
            raise ValueError(self.__name, _(u'Field is readonly'))

        datasheet.data[self.__name] = value
        datasheet.data = datasheet.data

    def __delete__(self, inst):
        datasheet = inst.datasheet
        if self.__name in datasheet.data:
            del datasheet.data[self.__name]
            datasheet.data = datasheet.data
