""" memphis.content tests setup """
from zope.component import hooks, eventtesting
from zope.component import testing as catesting

from memphis import config
from memphis.config.testing import tearDownConfig


def setUpCA(test):
    catesting.setUp(test)
    eventtesting.setUp(test)
    hooks.setHooks()


def tearDownCA(test):
    catesting.tearDown(test)
    tearDownConfig(test)
