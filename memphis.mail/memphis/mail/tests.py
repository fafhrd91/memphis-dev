""" tests setup """
import sys, unittest, doctest
from zope.sendmail.mailer import SMTPMailer

import memphis.config
from memphis.config import testing
from memphis.storage.testing import setUpDatastorage, tearDownDatastorage

from mailer import Mailer
from interfaces import IMailer


emails = []

def send(self, fromaddr, toaddr, message):
    if getattr(self, 'raiseError', False):
        raise ValueError

    if self.username:
        print "SMTP Auth selected"
    emails.append((fromaddr, toaddr, message))


def getEMails(clear=True):
    global emails
    m = list(emails)
    if clear:
        emails = []
    return m


def setUp(test):
    test.globs['getEMails'] = getEMails
    test.globs['SMTPMailer'] = SMTPMailer
    memphis.config.loadPackage('memphis.mail')
    setUpDatastorage(test)
    testing.setUpTestAsModule(test, 'memphis.TESTS')
    memphis.TESTS = sys.modules['memphis.TESTS']

    mailer = Mailer()
    mailer.hostname = 'localhost'
    mailer.port = 25
    mailer.email_from_name = u'Portal administrator'
    mailer.email_from_address = u'portal@z3ext.net'
    mailer.errors_address = ''
    test.oldsend = SMTPMailer.send
    SMTPMailer.send = send


def tearDown(test):
    SMTPMailer.send = test.oldsend
    tearDownDatastorage(test)
    testing.tearDownTestAsModule(test)
    del memphis.TESTS


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'template.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocFileSuite(
            'mailer.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))
