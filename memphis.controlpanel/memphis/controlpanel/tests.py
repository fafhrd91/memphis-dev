""" tests setup """
import sys, unittest, doctest
import memphis.config
from memphis.config import testing
from memphis.storage.testing import setUpDatastorage, tearDownDatastorage


def setUp(test):
    memphis.config.loadPackage('memphis.controlpanel')
    setUpDatastorage(test)
    testing.setUpTestAsModule(test, 'memphis.TESTS')
    memphis.TESTS = sys.modules['memphis.TESTS']


def tearDown(test):
    tearDownDatastorage(test)
    testing.tearDownTestAsModule(test)
    del memphis.TESTS


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'memphis.controlpanel.configlettype',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))
