""" memphis.storage tests

$Id: tests.py 11786 2011-01-31 00:26:59Z fafhrd91 $
"""
import sys, unittest, doctest
from memphis.config.testing import setUpTestAsModule, tearDownTestAsModule
from testing import setUpCA, setUpDatastorage, tearDownDatastorage

import memphis.config
import memphis.storage


def setUp(test):
    memphis.config.loadPackage('memphis.storage')
    setUpDatastorage(test)
    setUpTestAsModule(test, 'memphis.storage.TESTS')
    memphis.storage.TESTS = sys.modules['memphis.storage.TESTS']


def setUpREADME(test):
    setUpCA(test)
    setUpTestAsModule(test, 'memphis.storage.TESTS')
    memphis.storage.TESTS = sys.modules['memphis.storage.TESTS']


def tearDown(test):
    tearDownDatastorage(test)
    tearDownTestAsModule(test)
    del memphis.storage.TESTS


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                './README.txt',
                setUp=setUpREADME, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocFileSuite(
                './relation.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocFileSuite(
                './schema.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocFileSuite(
                './behavior.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'memphis.storage.meta',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'memphis.storage.behavior',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'memphis.storage.datasheet',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
