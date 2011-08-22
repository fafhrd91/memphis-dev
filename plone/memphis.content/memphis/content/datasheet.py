""" datasheet implementation """
import sys
from zope import interface
from zope.schema import getFields
from BTrees.OOBTree import OOBTree

from interfaces import _, IDatasheet
from exceptions import DatasheetException

_marker = object()


class Datasheet(object):
    """
    >>> from zope import interface, schema

    >>> class IMyDatasheet1(interface.Interface):
    ...   title = schema.TextLine(title = u'Title', default=u'Unset')
    ...
    >>> class IMyDatasheet2(interface.Interface):
    ...   title = schema.TextLine(title = u'Title')

    >>> DatasheetClass1 = DatasheetType(
    ...    'mydatasheet1', IMyDatasheet1, title='MyDatasheet1')

    >>> DatasheetClass2 = DatasheetType(
    ...    'mydatasheet2', IMyDatasheet2, title='MyDatasheet2')

    >>> ds = DatasheetClass1()
    >>> ds.title = u'test'

    >>> ds1 = DatasheetClass1()
    >>> ds1.title
    u'Unset'

    >>> ds1.__load__(ds)
    >>> ds1.title
    u'test'

    >>> ds2 = DatasheetClass2()
    >>> ds2.__load__(ds)
    Traceback (most recent call last):
    ...
    DatasheetException: Can't load data from incompatible datasheet

    """

    def __init__(self, instance=None):
        if instance is None:
            data = {}
        else:
            data = instance.__datasheets__.get(self.__id__)
            if data is None:
                data = OOBTree()
                instance.__datasheets__[self.__id__] = data

        self.__data__ = data
        self.__instance__ = instance

    def __load__(self, datasheet):
        if self.__schema__ is not datasheet.__schema__:
            raise DatasheetException(
                "Can't load data from incompatible datasheet")

        for fieldId in getFields(self.__schema__):
            field = self.__schema__[fieldId]
            value = getattr(datasheet, fieldId, field.default)
            if value is not field.default:
                setattr(self, fieldId, value)


class DatasheetType(type):
    """ Metaclass for datasheets

    >>> from zope import interface, schema
    >>> from memphis.content import datasheet

    >>> class IMyDatasheet(interface.Interface):
    ...   title = schema.TextLine(title = u'Title')

    >>> class MyDatasheet(object):
    ...   pass

    >>> DatasheetClass = DatasheetType(
    ...    'mydatasheet', IMyDatasheet, Datasheet, MyDatasheet, 'MyDatasheet', '')

    New class avilable by it's cname in memphis.content.datasheet module

    >>> getattr(datasheet, 'Datasheet<mydatasheet>') is DatasheetClass
    True

    >>> ds = DatasheetClass()
    >>> ds
    <memphis.content.datasheet.Datasheet<mydatasheet> object at ...>

    >>> isinstance(ds, MyDatasheet)
    True

    >>> isinstance(ds, datasheet.Datasheet)
    True

    We also can use number of base classes

    >>> class MyDatasheet2(object):
    ...   pass

    >>> DatasheetClass = DatasheetType(
    ...    'mydatasheet', IMyDatasheet,
    ...     Datasheet, (MyDatasheet, MyDatasheet2,), 'MyDatasheet', '')

    >>> ds = DatasheetClass(None)
    >>> isinstance(ds, MyDatasheet2)
    True

    >>> ds.__title__
    'MyDatasheet'

    >>> ds.__title__ = 'test'
    Traceback (most recent call last):
    ...
    AttributeError: Can't set data property

    """

    def __new__(cls, name, schema, base=Datasheet, class_=None, *args, **kw):
        cname = '%s<%s>'%(base.__name__, name)
        if type(class_) is tuple:
            bases = class_ + (base,)
        elif class_ is not None:
            bases = (class_, base)
        else:
            bases = (base,)

        tp = type.__new__(cls, str(cname), bases, {})
        setattr(sys.modules['memphis.content.datasheet'], cname, tp)
        return tp

    def __init__(cls, name, schema, base=Datasheet,
                 class_=None, title='', description=''):
        for f_id in getFields(schema):
            if not hasattr(cls, f_id):
                setattr(cls, f_id, DatasheetProperty(schema[f_id]))

        interface.classImplements(cls, schema, IDatasheet)

        cls.__id__ = DataProperty(unicode(name))
        cls.__title__ = DataProperty(title)
        cls.__description__ = DataProperty(description)
        cls.__schema__ = schema


class DataProperty(object):

    def __init__(self, value):
        self.value = value

    def __get__(self, inst, klass):
        return self.value

    def __set__(self, inst, value):
        raise AttributeError("Can't set data property")


class DatasheetProperty(object):
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
    ...    attr1 = DatasheetProperty(field)

    >>> Content.attr1
    <memphis.content.datasheet.DatasheetProperty object at ...>

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

    >>> field.readonly = False
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

        value = inst.__data__.get(self.__name, _marker)
        if value is _marker:
            return self.__field.default

        return value

    def __set__(self, inst, value):
        field = self.__field.bind(inst)
        field.validate(value)
        if field.readonly and \
               inst.__data__.get(self.__name, _marker) is not _marker:
            raise ValueError(self.__name, _(u'Field is readonly'))

        inst.__data__[self.__name] = value

    def __delete__(self, inst):
        del inst.__data__[self.__name]
