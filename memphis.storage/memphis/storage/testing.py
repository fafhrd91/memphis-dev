""" memphis.storage tests setup

$Id: testing.py 11801 2011-01-31 06:25:03Z fafhrd91 $
"""
from zope.component import hooks, eventtesting
from zope.component import testing as catesting

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from memphis import config, storage
from memphis.storage import meta, registry
from memphis.config.testing import tearDownConfig


def setUpCA(test):
    catesting.setUp(test)
    eventtesting.setUp(test)
    hooks.setHooks()


def setUpDatastorage(test):
    setUpCA(test)

    config.addPackage('memphis.storage.meta')
    config.loadPackage('memphis.config')

    engine = create_engine('sqlite://')
    Session = sessionmaker()
    Session.configure(bind=engine)

    session = Session()

    config.begin()
    storage.setMetadata(sqlalchemy.MetaData())
    storage.initialize(engine, session)

    config.commit()
    session.commit()


def tearDownDatastorage(test):
    sqlalchemy.orm.clear_mappers()
    storage.setSession(None)
    storage.setMetadata(None)
    catesting.tearDown(test)
    tearDownConfig(test)
