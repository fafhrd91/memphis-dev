====================
Content types system
====================

This content types system is base on ``memphis.storage`` implementation

Define new content
------------------

   >>> from zope import interface, component, schema

To define new content type we need content schema and behavior. Let's
define schema::

   >>> class IMyContent(interface.Interface):
   ...     
   ...     title = schema.TextLine(
   ...         title = u'Title',
   ...         default = u'')
   ...     
   ...     param2 = schema.TextLine(
   ...         title = u'Param2',
   ...         default = u'')


Now define content behavior::

   >>> class MyContent(object):
   ...     interface.implements(IMyContent)
   ...     
   ...     def __init__(self, item):
   ...         self.item = item


`IMyContent` is schema that defines content type model.
`MyContent` class implements behavior of content type. Instances
of this class are non persistent, but implementation can use
datasheets for storing persistent informaiton.

Now we have to register new content type in a system::

   >>> from memphis.contenttype import api, interfaces

   >>> ct = api.registerContentType(
   ...     u'myContent', IMyContent, MyContent, title='My content')

   >>> ct
   <memphis.contenttype.contenttype.ContentType ...>

   >>> ct.name == u'myContent'
   True


This content type object available as named utility::

   >>> sm = component.getSiteManager()

   >>> ctContent = sm.getUtility(interfaces.IContentType, u'myContent')

   >>> ctContent.name, ctContent.specification, ctContent.title
   (u'myContent', <InterfaceClass memphis.contenttype.TESTS.IMyContent>, 'My content')

We can create content instance

   >>> content = ctContent.create()

   >>> IMyContent.providedBy(content)
   True

Content type for content object::

   >>> print interfaces.IContentType(content)
   <BoundContentType:memphis.contenttype.contenttype.ContentType myContent 'My content'>

Also newly created item has applied datasheets and behaviors if they
was provided to `registerContentType` method.

   >>> list(content.schemas)
   [u'content.item', u'content.type', u'content.type-myContent']

   >>> list(content.behaviors)
   [u'content.type-myContent', u'content.item', u'content.type']

   >>> ds = content.getDatasheet('content.item')
   >>> ds.title
   u''

We can provide default datasheets during creation time::

   >>> from memphis.storage import api as ms_api

   >>> sch = ms_api.getSchema(interfaces.IContentItem)

   >>> ds = sch.schemaType('')
   >>> ds.title = u'New content item'

   >>> content = ctContent.create(ds)
   >>> content.getDatasheet('content.item').title
   u'New content item'

Content item behavior is nothing more than location information (name, parent)
and title/description::

   >>> ci = interfaces.IContentItem(content)

Because this content item is not set to container both name and parent
are None::

   >>> ci.__name__, ci.__parent__
   (None, None)

Title and description fields are from `content.item` datasheet::

   >>> ci.title, ci.description
   (u'New content item', u'')


Content Type binding
--------------------

We can use content types for various tasks like adding new content, 
check availability of content type, etc. Content type should be bound to 
some context::

   >>> interfaces.IBoundContentType.providedBy(ctContent)
   False

   >>> print ctContent
   <ContentType:memphis.contenttype.contenttype.ContentType myContent 'My content'>

Now we need content container::

   >>> class IMyContainer(interfaces.IContentContainer):
   ...     pass

   >>> ctContainer = api.registerContentType(
   ...     u'myContainer', IMyContainer, title='My container')

   >>> container = ctContainer.create()

Now let's bind content type to container::

   >>> bctContent = ctContent.__bind__(container)
   
   >>> interfaces.IBoundContentType.providedBy(bctContent)
   True

   >>> print bctContent
   <BoundContentType:memphis.contenttype.contenttype.ContentType myContent 'My content'>


Content Type availability
-------------------------

Unbound content type is always unavailable. There are no any
checkers by default.

   >>> ctContent.isAvailable()
   False

   >>> bctContent.isAvailable()
   True

We can define new avilability checks. We need new adapter to
IContentTypeChecker interface. We define checker that fail if content
type name is 'failed.container'

   >>> class NameChecker(object):
   ...    interface.implements(interfaces.IContentTypeChecker)
   ...    component.adapts(interfaces.IContentType, interface.Interface)
   ...    
   ...    def __init__(self, contenttype, context):
   ...        self.contenttype = contenttype
   ...        self.context = context
   ...
   ...    def check(self):
   ...        return not (self.contenttype.name == 'failed.container')

   >>> sm.registerAdapter(NameChecker, name='mychecker')

   >>> bctContent.name = 'failed.container'
   >>> bctContent.isAvailable()
   False

   >>> bctContent.name = 'any'
   >>> bctContent.isAvailable()
   True

   >>> t = sm.unregisterAdapter(NameChecker, name='mychecker')


Adding Content
--------------

We can add content only if container can contain content types.
Let's user `myContainer` content type for this.

   >>> ctContainer = sm.getUtility(interfaces.IContentType, 'myContainer')

Unbound container can't contain any content

   >>> list(ctContainer.listContainedTypes())
   []

   >>> container = ctContainer.create()
   >>> container.getDatasheet('content.item').title = u'My Container'

   >>> bctContainer = ctContainer.__bind__(container)

#   >>> [ct.name for ct in bctContainer.listContainedTypes()]
#   [u'myContent', u'myContainer']

#   >>> list(ctContainer.__bind__(object()).listContainedTypes())
#   []

#   >>> content = ctContent.create('Title')

Content type 'create' method determine content constructor arguments,
also it set schema fields

#   >>> ctContent.klass = None
#   >>> content = ctContent.create('Title')
#   Traceback (most recent call last):
#   ...
#   ValueError: Can't create content type: 'myContent'

#   >>> ctContent.klass = MyContent

#   >>> c = ctContent.create(param='param', param2='param2')
#   Traceback (most recent call last):
#   ...
#   TypeError: Not enough arguments

#   >>> c = ctContent.create('Title', param='param', param2='param2')
#   >>> c, c.param, c.param2
#   (<z3ext.content.TESTS.MyContent ...>, 'param', 'param2')


We can't add content with unbound content type

#   >>> ctContent.add(content, 'test-content')
#   Traceback (most recent call last):
#   ...
#   Unauthorized: Can't add 'myContent' content

#   >>> bctContent = ctContent.__bind__(container)
#   >>> addedContent = bctContent.add(content, 'test-content')
#   >>> addedContent.__name__
#   u'test-content'

#   >>> container[u'test-content'] is content
#   True


If container marked as IContainerNamesContainer, container select
content name

#   >>> from zope.container.interfaces import IContainerNamesContainer
#   >>> interface.alsoProvides(container, IContainerNamesContainer)
#   >>> addedContent = bctContent.add(content, 'test-content-name')
#   >>> addedContent.__name__
#   u'MyContent'

#   >>> interface.noLongerProvides(container, IContainerNamesContainer)


Before adding, contenttype checks if content 'isAddable'

#   >>> component.provideAdapter(NameChecker, name='mychecker')

#   >>> bctContent.name = 'failed.container'
#   >>> bctContent.isAddable()
#   False

#   >>> addedContent = bctContent.add(content, 'test-content')
#   Traceback (most recent call last):
#   ...
#   Unauthorized: Can't add 'failed.container' content

#   >>> t = sm.unregisterAdapter(NameChecker, name='mychecker')


Also we can't add content to not IContentContainer container

#   >>> ctContent.__bind__(object()).add(content, 'test-content')
#   Traceback (most recent call last):
#   ...
#   ValueError: Can't add content.

But if conten type not in container content type types listing we won't 
able to add content.

#   >>> interface.directlyProvides(ctContent, interfaces.IInactiveType)
#   >>> t = sm.unregisterUtility(ctContent, interfaces.IActiveType, ctContent.name)
   
#   >>> [ct.name for ct in bctContainer.listContainedTypes()]
#   [u'myContainer']

#   >>> content = ctContent.create(u'Title')
   
#   >>> addedContent = bctContent.add(content, 'test-content2')
#   Traceback (most recent call last):
#   ...
#   InvalidItemType: ...


ContentType Type
----------------

We can use any number of types in type attribute of directive. 
By default package defines some types.

IInactiveType - for inactive types, this type can't be added to any container
also if we won't use 'factory' then content type marked as inactive automaticly

#   >>> ct = component.getUtility(interfaces.IContentType, 'myContent')
#   >>> interfaces.IInactiveType.providedBy(ct)
#   True

#   >>> [ct.name for ct in bctContainer.listContainedTypes()]
#   [u'myContainer']


IActiveType - for content that can be added to any content container

#   >>> class IContent1(interfaces.IItem):
#   ...     pass

#   >>> class Content1(item.Item):
#   ...     interface.implements(IContent1)

#   >>> context = xmlconfig.string("""
#   ... <configure xmlns:z3ext="http://namespaces.zope.org/z3ext" i18n_domain="z3ext">
#   ...   <z3ext:content
#   ...     name="content1"
#   ...     title="content1"
#   ...     schema="z3ext.content.TESTS.IContent1"
#   ...     class="z3ext.content.TESTS.Content1"
#   ...     type="z3ext.content.type.interfaces.IActiveType"
#   ...     description="Simple content type." />
#   ... </configure>""", context)

#   >>> [ct.name for ct in bctContainer.listContainedTypes()]
#   [u'myContainer', u'content1']


`IExplicitlyAddable` - if content type is explicitly addable then it can be added 
only to container that explicitly contains content type

#   >>> class IContent2(interfaces.IItem):
#   ...     pass

#   >>> class Content2(item.Item):
#   ...     interface.implements(IContent2)

#   >>> context = xmlconfig.string("""
#   ... <configure xmlns:z3ext="http://namespaces.zope.org/z3ext" i18n_domain="z3ext">
#   ...   <z3ext:content
#   ...     name="content2"
#   ...     title="content2"
#   ...     schema="z3ext.content.TESTS.IContent2"
#   ...     class="z3ext.content.TESTS.Content2"
#   ...     type="z3ext.content.type.tests.ITestContentType
#   ...           z3ext.content.type.interfaces.IExplicitlyAddable"
#   ...     description="Simple content type." />
#   ... </configure>""", context)

#   >>> [ct.name for ct in bctContainer.listContainedTypes()]
#   [u'myContainer', u'content1']

Now let's add content type to precondition, it is the same if we use
`contains="mypackage.interface.IMyType"`

#   >>> precondition = component.getUtility(
#   ...     constraints.IItemTypePrecondition, bctContainer.name)
#   >>> precondition.ifaces.append(tests.ITestContentType)

#   >>> [ct.name for ct in bctContainer.listContainedTypes()]
#   [u'myContainer', u'content1', u'content2']
