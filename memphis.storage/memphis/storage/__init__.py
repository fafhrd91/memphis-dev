# memphis.storage public API

from memphis import config
from memphis.storage.item import Item

from memphis.storage.schema import Schema
from memphis.storage.interfaces import ISchema

from memphis.storage.relation import Relation
from memphis.storage.hooks import setSession
from memphis.storage.hooks import getSession
from memphis.storage.hooks import setMetadata
from memphis.storage.hooks import getMetadata

# storage registry api
from memphis.storage.registry import getSchema
from memphis.storage.registry import getBehavior
from memphis.storage.registry import getRelation
from memphis.storage.registry import querySchema
from memphis.storage.registry import queryBehavior
from memphis.storage.registry import registerSchema
from memphis.storage.registry import registerBehavior
from memphis.storage.registry import registerRelation

# base behavior classes
from memphis.storage.behavior import BehaviorBase
from memphis.storage.behavior import BehaviorFactoryBase
from memphis.storage.interfaces import IBehavior

# column generations
from memphis.storage.table import mapFieldToColumns

# schema/behavior wrappers
from memphis.storage.interfaces import ISchemaWrapper
from memphis.storage.interfaces import IBehaviorWrapper

# exceptions
from memphis.storage.exceptions import BehaviorException
from memphis.storage.exceptions import BehaviorNotFound
from memphis.storage.exceptions import SchemaNotFound
from memphis.storage.exceptions import StorageException

#events
from memphis.storage.interfaces import IBehaviorRemovedEvent
from memphis.storage.interfaces import IStorageInitializedEvent

#directives
from memphis.storage.directives import schema, relation, behavior

getItem = Item.getItem
insertItem = Item.insertItem
listItems = Item.listItems


def initialize(engine, session, models=True):
    setSession(session)
    MetaData = getMetadata()
    MetaData.bind = engine

    if models:
        from memphis.storage.models import initializeModels

        initializeModels(MetaData)

    MetaData.create_all(engine)

    def _create():
        import zope.event
        from interfaces import StorageInitializedEvent
        zope.event.notify(StorageInitializedEvent(MetaData))

        session.flush()

    config.addAction(
        discriminator = ('memphis.storage:initialize',),
        callable=_create)
