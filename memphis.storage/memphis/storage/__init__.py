# This file is necessary to make this directory a package.

from memphis import config
from memphis.storage.item import Item
from memphis.storage.schema import Schema
from memphis.storage.relation import Relation
from memphis.storage.hooks import setSession
from memphis.storage.hooks import getSession
from memphis.storage.hooks import setMetadata
from memphis.storage.hooks import getMetadata
from memphis.storage.registry import getSchema
from memphis.storage.registry import getBehavior
from memphis.storage.registry import getRelation
from memphis.storage.registry import querySchema
from memphis.storage.registry import queryBehavior
from memphis.storage.registry import registerSchema
from memphis.storage.registry import registerBehavior
from memphis.storage.registry import registerRelation
from memphis.storage.models import initializeModels

from exceptions import BehaviorException
from exceptions import BehaviorNotFound
from exceptions import SchemaNotFound
from exceptions import StorageException

#directives
from memphis.storage.directives import schema, relation, behavior

getItem = Item.getItem
insertItem = Item.insertItem


def initialize(engine, models=True):
    MetaData = getMetadata()
    MetaData.bind = engine

    if models:
        initializeModels(MetaData)

    MetaData.create_all(engine)

    def _create():
        session = getSession()
        if session is not None:
            session.flush()

    config.addAction(
        discriminator = ('memphis.storage:initialize',),
        callable=_create)


class BehaviorBase(object):

    def __init__(self, context, relation=None):
        self.context = context
        self.relation = relation


class BehaviorFactoryBase(object):
    pass
