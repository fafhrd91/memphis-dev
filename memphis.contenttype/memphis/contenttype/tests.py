"""

$Id: tests.py 11761 2011-01-29 15:21:40Z fafhrd91 $
"""
import sys, unittest, doctest

from zope import interface, schema, component
from zope.component import getSiteManager
from memphis.storage import api, config, interfaces
from memphis.storage.tests import setUpDatastorage, tearDownDatastorage
from memphis.storage.tests import setUpTestAsModule, tearDownTestAsModule

from memphis.contenttype import api


class ITestContent1(interface.Interface):

    field1 = schema.TextLine(
        title = u'Field1',
        required = False)

    field2 = schema.TextLine(
        title = u'Field2',
        required = False)

    field3 = schema.TextLine(
        title = u'Field3',
        required = False)

    field4 = schema.TextLine(
        title = u'Field4',
        required = False)

    field5 = schema.TextLine(
        title = u'Field5',
        required = False)


class ITestContent2(interface.Interface):

    field1 = schema.TextLine(
        title = u'Field6',
        required = False)

    field2 = schema.TextLine(
        title = u'Field7',
        required = False)

    field3 = schema.TextLine(
        title = u'Field8',
        required = False)

    field4 = schema.TextLine(
        title = u'Field9',
        required = False)

    field5 = schema.TextLine(
        title = u'Field10',
        required = False)


def setUp(test):
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
            doctest.DocFileSuite(
                './container.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'memphis.contenttype.root',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
