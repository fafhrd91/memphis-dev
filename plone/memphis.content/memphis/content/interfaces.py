""" memphis content interfaces """
from zope import interface, schema
from zope.component.interfaces import IObjectEvent, ObjectEvent
from zope.dublincore.interfaces import IDCDescriptiveProperties, IDCTimes
from zope.i18nmessageid import MessageFactory

from memphis.content import directives as api

_ = MessageFactory('memphis.content')


class IInstance(interface.Interface):

    __type__ = interface.Attribute('ITypeInformation object')

    oid = interface.Attribute('OID')

    behaviors = interface.Attribute('Instance behaviors')

    schemas = interface.Attribute('Instance schemas')

    def getDatasheet(name):
        """ datasheet """


class ISchema(interface.Interface):
    """ schema interface """

    name = interface.Attribute('Name')

    title = interface.Attribute('Title')

    description = interface.Attribute('Description')

    schema = interface.Attribute('Schema')

    def __call__(item):
        """ create datasheet """


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

    __context__ = interface.Attribute('Instance')

    __behavior__ = interface.Attribute('IBehavior object')


class IDatasheet(interface.Interface):
    """ datasheet """
    
    __id__ = interface.Attribute('Id')
    __title__ = interface.Attribute('Title')
    __description__ = interface.Attribute('Description')
    __schema__ = interface.Attribute('Schema')

    __data__ = interface.Attribute('Data dictionary')
    __instance__ = interface.Attribute('Instance')


# content system
class IContent(interface.Interface):
    """ base content behavior """


class IContentSchema(IDCDescriptiveProperties, IDCTimes):
    """ behavior interface for content types """
    api.schema('content.instance', title = 'Content instance')

    title = schema.TextLine(
        title = _(u'Title'),
        default = u'',
        missing_value = u'',
        required = True)

    description = schema.Text(
        title = _(u'Summary'),
        description = _(u'Brief summary of your content item.'),
        default = u'',
        missing_value = u'',
        required = False)

    created = interface.Attribute(u'Creation Date')
    modified = interface.Attribute(u'Modification Date')


class IContentType(interface.Interface):
    """ content type interface """
        
    type = interface.Attribute('Primary behavior')

    factory = interface.Attribute('Content factory')

    behaviors = interface.Attribute('Behaviors')

    schemas = interface.Attribute('Schemas')

    def create(**data):
        """ create new content item """

    def applyBehavior(*args):
        """ apply behaviors """

    def removeBehavior(*args):
        """ remove behaviors """

    def applySchema(sch):
        """ apply schema """

    def removeSchema(sch):
        """ remove schema """


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
