===========
DataStorage
===========

fixme: need ad high level description here


Setup storage
=============

Before we can use storage we have to configure it. It requires
database engine and sqlalchemy session. Let' configure storage with 
in-memory sqlite database::

    >>> from memphis import config, storage
    >>> from memphis.storage import interfaces

Before do any configuration we should begin configuration procedure::

    >>> config.begin()

To be able to use storage decorators, like `schema`, `relation`, `behavior`,
we have to explicite add package to configuraton system. `loadPackage`
load all dependecies into configuraton system::

    >>> config.loadPackage('memphis.storage')

Well, you don't need to do this for `memphis.storage` package, but for
any other package that uses `memphis.storage` you should.

Now system is ready for configuration::

    >>> from sqlalchemy import create_engine
    >>> from sqlalchemy.orm import sessionmaker

    >>> engine = create_engine('sqlite://')
    >>> Session = sessionmaker()
    >>> Session.configure(bind=engine)
    >>> session = Session()

You have to initialize storage with this engine, this should be done during
application initialization::

    >>> storage.initialize(engine)

Now you should commit configuration settings. You should register
all required relations, schemas, behavior before commiting config.
This should be done during application initialization::

    >>> config.commit()

For each transaction in your application you should set storage session.
For example if you use pyramid and pyramid_sqla, add INewRequest handler::

    # from pyramid_sqla
    #
    # @component.adapter(INewRequest)
    # def newRequestHandler(event):
    #    storage.setSession(pyramid_sqla.get_session())

    >>> storage.setSession(session)

System creates database entities during initialization, so don't forget
to commit session after initialization::

    >>> session.commit()

That's it. Now we can use storage::

    >>> item = storage.insertItem()

    >>> item
    <memphis.storage.item.Item object at ...>


Schema
======

Schema is model in orm term. But it doesn't contain any application logic,
it is just storage for data. You apply any schema to any item. Memphis storage
uses `zope.schema` for schema definition::

    >>> from zope import interface, schema, component

    >>> class IMySchema(interface.Interface):
    ...     storage.schema('myschema', title=u'My schema')
    ...     
    ...     title = schema.TextLine(
    ...         title = u'Title',
    ...         required = True,
    ...         default = u'No value')

We need reload info into system, but this is required only
if new registrations are added during runtime::

    >>> reGrok()

`storage.schema` is decarator that register schema, but it possible to
use `registerSchema` function::

    # storage.registerSchema('myschema', IMySchema, title='My schema')


Actually, that's it. This call register named utility and create sql
table behind the scene. You can start use it immediately::

    >>> item.applySchema(IMySchema)

Actual record of schema is called 'datasheet'::

    >>> datasheet = item.getDatasheet(IMySchema)
    >>> datasheet.title
    u'No value'

To modify datasheet attribute just change attribute value::

    >>> datasheet.title = u'New title value'
    >>> datasheet.title
    u'New title value'


But you should flush session if you want reflect new values into
database. Usually this is done by sqlalchemy transaction manager like
`pyramid_sqla`::

    >>> session.flush()

    >>> datasheet = item.getDatasheet(IMySchema)
    >>> datasheet.title
    u'New title value'

Datasheet class implements your schema. For example you can use datasheet
as context for edit form::

    >>> IMySchema.providedBy(datasheet)
    True


Schema query
------------

First of all you can get all applied schemas for item::

    >>> item.schemas
    [u'myschema']

`ISchema` object provides special method `query` for model quering. It is
just wrapper for sqlalchemy `query().filter()`::

    >>> schemaOb = storage.getSchema(IMySchema)
    >>> q = schemaOb.query(schemaOb.Type.title == 'New title value')
    >>> q
    <sqlalchemy.orm.query.Query object at ...>

    >>> list(q)
    [<memphis.storage.datasheet.Datasheet<myschema> object at ...>]

schemaOb.Type is sqlalchemy table that is generated for
IMySchema schema, so you can use any kind of quering that is supported
by `sqlalchemy`.


Custom model implementation
---------------------------

There is one requirenment for custom model, it should have `oid`
column and it should be foreign key to `items.oid` and mapper class
constructor should accept one parameter `oid`::

    >>> import sqlalchemy

    >>> table = sqlalchemy.Table(
    ...     'mycustomtable', storage.getMetadata(),
    ...     sqlalchemy.Column(
    ...         'oid', sqlalchemy.Unicode(32),
    ...         sqlalchemy.ForeignKey('items.oid'), primary_key=True),
    ...     sqlalchemy.Column(
    ...         'title', sqlalchemy.Unicode(255)))

    >>> class MyCustomSchemaItem(object):
    ...     
    ...     def __init__(self, oid):
    ...         self.oid = oid
    ...         self.title = u'No new value'

    >>> mapper = sqlalchemy.orm.mapper(MyCustomSchemaItem, table)


    >>> class IMyCustomSchema(interface.Interface):
    ...     storage.schema('mycustomschema', MyCustomSchemaItem)
    ...     
    ...     title = schema.TextLine(
    ...         title = u'Title',
    ...         required = True,
    ...         default = u'No new value')

    >>> reGrok()

Now we can apply schema::

    >>> item.applySchema(IMyCustomSchema)

    >>> datasheet = item.getDatasheet(IMyCustomSchema)
    >>> datasheet.title = u'New title value'
    >>> session.flush()

    >>> datasheet = item.getDatasheet(IMyCustomSchema)
    >>> datasheet.title
    u'New title value'


Behavior
========

Behavior is actual implementaion of some behavior. You can apply `behavior`
to any item in system. Behavior should accept `item` as first parameter
and `relation` as second if behavior use relation. but behavior is not
limited with one relation, it can use any number of relations or schemas.
Behavior factory can implement two methods. `applyBehavior` is called
when behavior is applied to item and 'removeBehavior` is called right
behore removing behavior, so you can add additional initialization or
schema to item, or prevent of removing behavior.


Let's define very basic container/contained behavior::

    >>> class IContained(interface.Interface):
    ...     __name__ = interface.Attribute('Name')
    ...     __parent__ = interface.Attribute('Parent')

    >>> class IContainer(interface.Interface):
    ...     """ simple container behavior """

Also lets use schema::

    >>> class IContainerSchema(interface.Interface):
    ...     storage.schema('container')
    ...     
    ...     title = schema.TextLine(
    ...         title = u'Container title',
    ...         default = u'No title')


We will use relation for container implementaion, more detail on
relations later::

    >>> class IContainerRelation(interface.Interface):
    ...     storage.relation('container')
    ...     
    ...     name = schema.TextLine(
    ...         title = u'Item name')


Now implementation::

    >>> class Contained(storage.BehaviorBase):
    ...     storage.behavior('contained', IContained, IContainerRelation)
    ...     
    ...     def __init__(self, context, relation):
    ...         super(Contained, self).__init__(context, relation)
    ...         
    ...         self.context = context
    ...         self.relation = relation
    ...         
    ...         rel = self.relation.getReferences(
    ...             destination=self.context.oid).next()
    ...         
    ...         self.__name__ = rel.name
    ...         self.__parent__ = rel.__source__

    >>> class Container(storage.BehaviorBase):
    ...     storage.behavior('container', IContainer, IContainerRelation,
    ...                      IContainerSchema,
    ...                      title = 'Conainer implementaion')
    ...         
    ...     def keys(self):
    ...         return [rel.name for rel in
    ...                 self.__relation__.getReferences(self.context.oid)]
    ...     
    ...     def __getitem__(self, name):
    ...         try:
    ...             rel = self.__relation__.getReferences(
    ...                 self.context.oid, name=name).next()
    ...             return rel.__destination__
    ...         except StopIteration:
    ...             pass
    ...         raise KeyError(name)
    ...     
    ...     def __setitem__(self, name, item):
    ...         if not IContained.providedBy(item):
    ...             item.applyBehavior('contained')
    ...         
    ...         self.__relation__.insert(self.context.oid, item.oid, name=name)
    ...         
    >>> reGrok()

To use `storage.behavior` decorator your behavior class has to inherite
from `storage.BehaviorBase` class.

Alternative registration method, in this case `storage.BehaviorBase` is
not required::

    # storage.registerRelation(
    #    'container', IContainerRelation)
    # bh = storage.registerBehavior(
    #    'container', IContainer, Container, relation = 'container')
    # bh = storage.registerBehavior(
    #    'contained', IContained, Contained, relation = 'container')


Now we can create container::

    >>> itemCont = storage.insertItem()
    >>> itemCont.applyBehavior('container')

    >>> IContainer.providedBy(itemCont)
    True

There is one specific issue, behavior interface is provided by item,
but it not implement it. So to get actual implementation you have to
adapt item to behavior interface::

    >>> container = IContainer(itemCont)

    >>> isinstance(container, Container)
    True

Let's add item to container and do some operations::

    >>> item = storage.insertItem()

    >>> container['myitem'] = item

    >>> container.keys()
    [u'myitem']

    >>> IContained(item).__name__
    u'myitem'

    >>> IContained(item).__parent__.oid == itemCont.oid
    True

    >>> container['myitem'].oid == item.oid
    True

Full implementation of container is available
in ``memphis\storage\container.py``.

If behavior declare schema usage, behavior can access schema datasheet as
behavior attributes::

    >>> itemCont.schemas
    [u'container']

    >>> datasheet = itemCont.getDatasheet(IContainerSchema)
    >>> datasheet.title
    u'No title'
    >>> container.title
    u'No title'

    >>> container.title = u'Container title'
    >>> datasheet.title
    u'Container title'


Relation
========

Relation is one-to-many relation. any item can have relation to any
other item. Relations are named. Relation can have additional
attribute. Basicly relation has similar implementation to schemas.
Let's use `container` relation from previos section. Relation can be accessed
with `memphis.storage.getRelation` api call::

    >>> rel = storage.getRelation(IContainerRelation)

Relatin has some basic method like `get`, `insert`, `remove`, `getReferences`.
Each reference has `oid` of this relation. Let's find container references
for item::

    >>> relItem = list(rel.getReferences(itemCont.oid))[0]
    >>> relItem.oid
    u'...'

Because `container` relation defined with IContainerRelation schema,
relation item has `name` attribute::

    >>> relItem.name
    u'myitem'


Query
-----

Relation queries work same as schema queries.
You can get list of all item relations::

    >>> from memphis.storage.relation import Relation
    
    >>> list(Relation.getItemReferences(itemCont.oid))
    [<memphis.storage.relation.Reference object at ...>]
    
or

    >>> list(itemCont.getReferences())
    [<memphis.storage.relation.Reference object at ...>]

    >>> relItem = list(Relation.getItemReferences(itemCont.oid))[0]
    >>> relItem.__source__.oid == itemCont.oid
    True
    >>> relItem.__destination__.oid == item.oid
    True

Also it's possible to get all back relations for item::

    >>> brelItem = list(Relation.getItemBackReferences(item.oid))[0]
    >>> brelItem.oid == relItem.oid
    True

or 

    >>> brelItem = list(item.getBackReferences())[0]
    >>> brelItem.oid == relItem.oid
    True

Relation instance provides special method `query` for model quering. It is
just wrapper for sqlalchemy `query().filter()`::

    >>> q = rel.query(rel.Type.name == 'myitem')
    >>> q
    <sqlalchemy.orm.query.Query object at ...>

    >>> list(q)
    [<memphis.storage.datasheet.Reference<container> object at ...>]

rel.Type is sqlalchemy mapped to table class that is generated for
IContainerRelation schema, so you can use any kind of quering that is supported
by `sqlalchemy`.


Custom model implementation
---------------------------

Same as for schema, you can use your own model for relation.
There is requirenment for custom model, it should have `oid`, `source`
and `destination` columns and it's `source` and `destination` columns
should be foreign key to `items.oid`. simplest solution for class is inherit
from relation.Reference class::

    >>> import sqlalchemy

    >>> table = sqlalchemy.Table(
    ...     'mycustomrel', storage.getMetadata(),
    ...     sqlalchemy.Column('oid', sqlalchemy.Unicode(32), primary_key=True),
    ...     sqlalchemy.Column('source', sqlalchemy.Unicode(32),
    ...                       sqlalchemy.ForeignKey('items.oid')),
    ...     sqlalchemy.Column('destination', sqlalchemy.Unicode(32),
    ...                       sqlalchemy.ForeignKey('items.oid')),
    ...     sqlalchemy.Column(
    ...         'title', sqlalchemy.Unicode(255)))

    >>> from memphis.storage.relation import Reference

    >>> class MyCustomItem(Reference):
    ...     pass

    >>> mapper = sqlalchemy.orm.mapper(MyCustomItem, table)


    >>> class IMyCustomRel(interface.Interface):
    ...     storage.relation('mycustomrel', MyCustomItem)
    ...     
    ...     title = schema.TextLine(
    ...         title = u'Title',
    ...         required = True,
    ...         default = u'No new value')

    >>> reGrok()

Now we can use relation::

    >>> rel = storage.getRelation(IMyCustomRel)

    >>> relItem = rel.insert(item.oid, itemCont.oid, title = 'Relation title')
    >>> relItem.title
    'Relation title'

    >>> list(rel.query(MyCustomItem.title == 'Relation title'))
    [<memphis.storage.TESTS.MyCustomItem object at ...>]

