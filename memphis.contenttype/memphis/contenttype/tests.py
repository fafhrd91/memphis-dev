"""

$Id: tests.py 11761 2011-01-29 15:21:40Z fafhrd91 $
"""
import unittest, doctest
from memphis import config
from memphis.config.testing import setUpTestAsModule, tearDownTestAsModule
from memphis.storage.testing import setUpDatastorage, tearDownDatastorage


def setUp(test):
    config.loadPackage('memphis.contenttype')
    setUpDatastorage(test)
    setUpTestAsModule(test, 'memphis.TESTS')


def tearDown(test):
    tearDownDatastorage(test)
    tearDownTestAsModule(test)


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                './README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
