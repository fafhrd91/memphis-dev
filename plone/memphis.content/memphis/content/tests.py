""" memphis.storage tests """
import sys, unittest, doctest
import memphis.config
from memphis.config.testing import setUpTestAsModule, tearDownTestAsModule

import memphis.content
from memphis.content.testing import setUpCA, tearDownCA


def setUp(test):
    memphis.config.begin()
    memphis.config.loadPackage('memphis.content')
    setUpCA(test)
    setUpTestAsModule(test, 'memphis.content.TESTS')
    memphis.content.TESTS = sys.modules['memphis.content.TESTS']
    memphis.config.commit()


def tearDown(test):
    tearDownTestAsModule(test)
    tearDownCA(test)
    del memphis.content.TESTS


def test_suite():
    return unittest.TestSuite((
            #doctest.DocFileSuite(
            #    './README.txt',
            #    setUp=setUpREADME, tearDown=tearDown,
            #    optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocFileSuite(
                './behavior.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocFileSuite(
                './schema.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'memphis.content.meta',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'memphis.content.datasheet',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
