from zope import interface
from zope.component.interfaces import IObjectEvent, ObjectEvent


class IItem(interface.Interface):

    oid = interface.Attribute('OID')

    behaviors = interface.Attribute('Item behaviors')

    schemas = interface.Attribute('Applied schemas types')

    def applySchema(type):
        """ apply schema to item """

    def getDatasheet(type):
        """ datasheet """


class IRelation(interface.Interface):
    """ interface to relations, it doesn't have
    persistent state"""

    name = interface.Attribute('Relation name')

    title = interface.Attribute('Title')

    description = interface.Attribute('Description')

    schema = interface.Attribute('Schema')

    def query(oid, **kw):
        """ query relations """

    def getReferences(source=None, destination=None):
        """ """


class IReference(interface.Interface):
    """ relation item """

    oid = interface.Attribute('Reference OID')

    type = interface.Attribute('Relation type')

    __source__ = interface.Attribute('Source item')

    __destination__ = interface.Attribute('Destination item')


class ISchema(interface.Interface):
    """ schema interface """

    name = interface.Attribute('Name')

    title = interface.Attribute('Title')

    description = interface.Attribute('Description')

    schema = interface.Attribute('Schema')

    def __call__(item):
        """ create datasheet """


class ISchemaFieldMapper(interface.Interface):
    """ feild -> sqlalchemy column mapper """

    def __call__():
        """ return secuqence of sqlaclhemy.Column objects """


class IBehavior(interface.Interface):
    """ behavior info interface """

    name = interface.Attribute('Name')

    title = interface.Attribute('Title')

    description = interface.Attribute('Description')

    spec = interface.Attribute('Behavior interface')

    schema = interface.Attribute('Schema')

    factory = interface.Attribute('Factory')

    def apply(item):
        """ apply behavior to item """

    def remove(item):
        """ remove behavior from item """

    def __call__(item):
        """ create behavior for item """

    def getBehaviorOIDs():
        """ list all oids for this behavior """


class IBehaviorBase(interface.Interface):
    """ base behavior """

    __context__ = interface.Attribute('Storage item')

    __behavior__ = interface.Attribute('IBehavior object')

    __relation__ = interface.Attribute('Relation, if behavior uses relation')

    __datasheet__ = interface.Attribute('Datasheet, if behavior uses schema')

    oid = interface.Attribute('Storage item oid')


# wrappers
class ISchemaWrapper(interface.Interface):

    def wrapSchema(schema, item):
        """ wrap schema adapter """


class IBehaviorWrapper(interface.Interface):

    def wrapBehavior(behavior, item):
        """ wrap behavior adapter """


# events
class IBehaviorAppliedEvent(IObjectEvent):
    """ Behavior applied event """

    name = interface.Attribute('Behavior name')

    behavior = interface.Attribute('Behavior interface')


class BehaviorAppliedEvent(ObjectEvent):
    interface.implements(IBehaviorAppliedEvent)

    def __init__(self, item, name, behavior):
        self.object = item
        self.name = name
        self.behavior = behavior


class IBehaviorRemovedEvent(IObjectEvent):
    """ Behavior removed event """

    name = interface.Attribute('Behavior name')

    behavior = interface.Attribute('Behavior interface')


class BehaviorRemovedEvent(ObjectEvent):
    interface.implements(IBehaviorRemovedEvent)

    def __init__(self, item, name, behavior):
        self.object = item
        self.name = name
        self.behavior = behavior


class IStorageInitializedEvent(interface.Interface):
    """ storage initialized event """

    metadata = interface.Attribute('MetaData')


class StorageInitializedEvent(object):
    interface.implements(IStorageInitializedEvent)

    def __init__(self, metadata):
        self.metadata = metadata
