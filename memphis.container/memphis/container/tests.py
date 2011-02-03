"""

$Id: tests.py 4719 2011-02-03 01:47:46Z nikolay $
"""
import unittest, doctest
from memphis.storage import config
from memphis.config.tests import setUpTestAsModule, tearDownTestAsModule
from memphis.storage.tests import setUpDatastorage, tearDownDatastorage


def setUp(test):
    config.loadPackage('memphis.container')
    setUpDatastorage(test)
    setUpTestAsModule(test, 'memphis.TESTS')


def tearDown(test):
    tearDownDatastorage(test)
    tearDownTestAsModule(test)


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                './container.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            #doctest.DocTestSuite(
            #    'memphis.contenttype.root',
            #    setUp=setUp, tearDown=tearDown,
            #    optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
