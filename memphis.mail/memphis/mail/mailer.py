"""

$Id: mailer.py 11808 2011-01-31 06:54:22Z fafhrd91 $
"""
import logging
from zope import interface
from zope.sendmail.mailer import SMTPMailer
from memphis import config, controlpanel
from memphis.mail.interfaces import _, IMailer

logger = logging.getLogger('memphis.mail')


class Mailer(object):
    interface.implements(IMailer)

    def send(self, fromaddr, toaddrs, message):
        if self.disabled:
            logger.info("Tring to send mail, but mailer is disabled.")
            return

        # log message
        if self.log_emails:
            logger.log(logging.INFO, toaddrs)
            logger.log(logging.INFO, message)

        if self.smtpuser and self.smtppass:
            mailer = SMTPMailer(self.hostname, self.port,
                                self.smtpuser, self.smtppass)
        else:
            mailer = SMTPMailer(self.hostname, self.port)

        # delivery
        if self.no_delivery:
            logger.info("Mail delivery is disabled.")
            return

        try:
            mailer.send(fromaddr, toaddrs, message)
        except Exception, err:
            logger.exception(str(err))


config.action(
    controlpanel.registerConfiglet,
    'system.mail', IMailer, Mailer,
    _('Mail settings'), _('Configure portal mail settings.'))
