import sqlalchemy
from zope import interface
from zope.schema import getFields
from memphis.storage.hooks import getSession
from memphis.storage.interfaces import \
    IBehavior, IBehaviorBase, IBehaviorWrapper, ISchemaWrapper
from memphis.storage.exceptions import StorageException


class BehaviorBase(object):
    interface.implements(IBehaviorBase)

    __behavior__ = None
    __relation__ = None
    __datasheet__ = None

    def __init__(self, context, relation=None):
        self.__context__ = context
        self.__relation__ = relation
        if self.__behavior__.schema:
            if self.__wrapper__:
                from registry import getSchema
                self.__datasheet__ = getSchema(
                    self.__behavior__.schema).getDatasheet(self.__context__.oid)
            else:
                self.__datasheet__ = self.__context__.getDatasheet(
                    self.__behavior__.schema)
                
    @property
    def oid(self):
        return self.__context__.oid


class BehaviorFactoryBase(object):
    pass


class Behavior(object):
    interface.implements(IBehavior)

    def __init__(self, name, title, spec, relation, factory,
                 schema=None, description=''):
        self.name = name
        self.title = title
        self.description = description
        self.spec = spec
        self.schema = schema
        self.factory = factory
        self.relation = relation
        self.iswrapper = spec.isOrExtends(IBehaviorWrapper) or \
            spec.isOrExtends(ISchemaWrapper)

        if type(factory) is type and issubclass(factory, BehaviorBase):
            factory.__behavior__ = self
            factory.__wrapper__ = self.iswrapper

            if schema is not None:
                for f_id in getFields(schema):
                    if not hasattr(factory, f_id):
                        setattr(factory, f_id, BehaviorProperty(schema[f_id]))

    def apply(self, item):
        # run custom code
        if hasattr(self.factory, 'applyBehavior'):
            self.factory.applyBehavior(item, self)

        # apply behavior
        oid = item.oid
        session = getSession()

        ob = session.query(SQLBehavior).filter(
            sqlalchemy.and_(
                SQLBehavior.oid == oid, SQLBehavior.name == self.name)).first()
        if ob is not None:
            raise StorageException('Behavior already applied: %s'%self.name)

        if self.iswrapper:
            session.add(SQLBehavior(oid, self.name, -1))
        else:
            num = len(self.getItemBehaviors(oid)) + 1
            session.add(SQLBehavior(oid, self.name, num))
        session.flush()

        # apply schema
        if self.schema is not None:
            item.applySchema(self.schema)

    def remove(self, item):
        oid = item.oid
        session = getSession()

        # remove behaivor record
        ob = session.query(SQLBehavior).filter(
            sqlalchemy.and_(
                SQLBehavior.oid == oid, SQLBehavior.name == self.name)).first()

        if ob is None:
            raise StorageException('Behavior is not applied: %s'%self.name)

        session.delete(ob)

        # remove schema
        if self.schema is not None:
            item.removeSchema(self.schema)

        session.flush()

        if hasattr(self.factory, 'removeBehavior'):
            self.factory.removeBehavior(item, self)

    def __call__(self, item):
        from registry import getRelation

        if self.relation:
            return self.factory(
                item, getRelation(self.relation))
        else:
            return self.factory(item)

    def getBehaviorOIDs(self):
        for r in getSession().query(
            SQLBehavior.oid).filter(SQLBehavior.name == self.name):
            yield r[0]

    @classmethod
    def getItemBehaviors(self, oid):
        return [r[0] for r in getSession().query(
                SQLBehavior.name).filter(
                SQLBehavior.oid==oid).order_by(SQLBehavior.inst_id)]


class SQLBehavior(object):

    def __init__(self, oid, name, inst_id=None):
        self.oid = oid
        self.name = name
        self.inst_id = inst_id


_marker = object()

class BehaviorProperty(object):
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
    ...    attr1 = BehaviorProperty(field)

    >>> class Datasheet(object):
    ...     pass

    Lets create class instance and add field values storage

    >>> ob = Content()
    >>> ob.__datasheet__ = Datasheet()

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

    >>> ob.__datasheet__.attr1
    u'value1'

    If storage contains field value we shuld get it

    >>> ob.__datasheet__.attr1 = u'value2'
    >>> ob.attr1
    u'value2'

    We can't set value for readonly fields

    >>> field.readonly = True
    >>> ob.attr1 = u'value1'
    Traceback (most recent call last):
    ...
    ValueError: ('attr1', u'Field is readonly')

    >>> del ob.attr1
    >>> ob.__datasheet__.__dict__
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

        datasheet = inst.__datasheet__
        value = getattr(datasheet, self.__name, _marker)
        if value is _marker:
            return self.__field.default

        return value

    def __set__(self, inst, value):
        datasheet = inst.__datasheet__

        field = self.__field.bind(inst)
        field.validate(value)
        if field.readonly and \
               getattr(datasheet, self.__name, _marker) is not _marker:
            raise ValueError(self.__name, u'Field is readonly')

        setattr(datasheet, self.__name, value)

    def __delete__(self, inst):
        datasheet = inst.__datasheet__
        if hasattr(datasheet, self.__name):
            delattr(datasheet, self.__name)
