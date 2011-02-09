import sys, copy
from zope import interface
from zope.schema import getFields
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

    >>> ds = DatasheetClass1({})
    >>> ds.title = u'test'

    >>> ds1 = DatasheetClass1({})
    >>> ds1.title
    u'Unset'

    >>> ds1.__load__(ds)
    >>> ds1.title
    u'test'

    >>> ds2 = DatasheetClass2({})
    >>> ds2.__load__(ds)
    Traceback (most recent call last):
    ...
    DatasheetException: Can't load data from incompatible datasheet

    """
    def __init__(self, oid=''):
        self.oid = oid

        # update defaults
        sch = self.__schema__
        for field in getFields(sch):
            setattr(self, field, copy.copy(sch[field].default))

    def __load__(self, datasheet):
        if self.__schema__ is not datasheet.__schema__:
            raise DatasheetException(
                "Can't load data from incompatible datasheet")

        for field in getFields(self.__schema__):
            setattr(self, field, getattr(datasheet, field))


class DatasheetType(type):
    """ Metaclass for datasheets

    >>> from zope import interface, schema
    >>> from memphis.storage import datasheet

    >>> class IMyDatasheet(interface.Interface):
    ...   title = schema.TextLine(title = u'Title')

    >>> class MyDatasheet(object):
    ...   pass

    >>> DatasheetClass = DatasheetType(
    ...    'mydatasheet', IMyDatasheet, Datasheet, MyDatasheet, 'MyDatasheet', '')

    New class avilable by it's cname in memphis.storage.datasheet module

    >>> getattr(datasheet, 'Datasheet<mydatasheet>') is DatasheetClass
    True

    >>> ds = DatasheetClass({})
    >>> ds
    <memphis.storage.datasheet.Datasheet<mydatasheet> object at ...>

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

    >>> ds = DatasheetClass({})
    >>> isinstance(ds, MyDatasheet2)
    True

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
        setattr(sys.modules['memphis.storage.datasheet'], cname, tp)
        return tp

    def __init__(cls, name, schema, base=Datasheet,
                 class_=None, title='', description=''):
        if schema is not None:
            for f_id in getFields(schema):
                if not hasattr(cls, f_id):
                    setattr(cls, f_id, copy.copy(schema[f_id].default))

            interface.classImplements(cls, schema)

        cls.__id__ = DataProperty(unicode(name))
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
