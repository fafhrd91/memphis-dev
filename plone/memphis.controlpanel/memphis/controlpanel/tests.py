""" memphis.storage tests """
import sys, unittest, doctest
from zope.component import getSiteManager
from zope.component.hooks import setSite

import memphis
from memphis import config
from memphis.config import testing


class Site(object):

    def __init__(self, sm):
        self.sm = sm

    def getSiteManager(self):
        return self.sm

    @property
    def aq_base(self):
        return self


def setUp(test):
    memphis.config.loadPackage('memphis.controlpanel')
    testing.setUpConfig(test)
    testing.setUpTestAsModule(test, 'memphis.TESTS')
    memphis.TESTS = sys.modules['memphis.TESTS']
    memphis.config.commit()
    setSite(Site(getSiteManager()))


def tearDown(test):
    setSite(Site(None))
    testing.tearDownTestAsModule(test)
    testing.tearDownConfig(test)
    del memphis.TESTS


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'memphis.controlpanel.cptype',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'memphis.controlpanel.cmfpatches',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'memphis.controlpanel.views',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
