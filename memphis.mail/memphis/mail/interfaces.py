""" memphis.mail interfaces

$Id: interfaces.py 11808 2011-01-31 06:54:22Z fafhrd91 $
"""
from zope import schema, interface
from zope.sendmail.interfaces import IMailDelivery
from z3c.schema.email import RFC822MailAddress
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('memphis.mail')


class IMailer(IMailDelivery):

    hostname = schema.TextLine(
        title = _(u'SMTP server'),
        description = _(u'The address of your local SMTP (outgoing e-mail) '
                        u'server. Usually "localhost", unless you use an '
                        u'external server to send e-mail.'),
        default = u'localhost',
        required = True)

    port = schema.Int(
        title = _(u'SMTP Port'),
        description = _(u'The port of your local SMTP (outgoing e-mail) '
                        u'server. Usually "25".'),
        default = 25,
        required = True)

    smtpuser = schema.TextLine(
        title=_(u"Username"),
        description=_(u"Username used for optional SMTP authentication."),
        default=u'',
        required=False)

    smtppass = schema.Password(
        title=_(u"Password"),
        description=_(u"Password used for optional SMTP authentication."),
        default=u'',
        required=False)

    email_from_name = schema.TextLine(
        title = _(u"Site 'From' name"),
        description = _(u'Portal generates e-mail using this name '
                        u'as the e-mail sender.'),
        default = u'Portal administrator',
        required = True)

    email_from_address = RFC822MailAddress(
        title = _(u"Site 'From' address"),
        description = _(u'Portal generates e-mail using this address '
                        u'as the e-mail return address.'),
        default = u'portal@localhost.local',
        required = True)

    errors_address = RFC822MailAddress(
        title = _(u"Site 'Errors' address"),
        description = _(u'Portal generates e-mail using this address '
                        u'as the errors handler address.'),
        required = False)

    log_emails = schema.Bool(
        title = _(u'Log messages'),
        description= _(u'Log email address and message.'),
        default = False)

    disabled = schema.Bool(
        title = _(u'Disabled'),
        description = _(u'Disable sending message.'),
        default = False)


class IMailTemplate(interface.Interface):
    """ mail template """

    charset = interface.Attribute('Charset')

    contentType = interface.Attribute('Message content type')

    messageId = interface.Attribute('Unique Message ID')

    template = interface.Attribute('Template')

    from_name = interface.Attribute('From name')

    from_address = interface.Attribute('From address')

    to_address = interface.Attribute('To address')

    return_address = interface.Attribute('Return address')

    errors_address = interface.Attribute('Erorrs Address')


    def __init__(context, request):
        """ multi adapter """

    def addHeader(header, value, encode=False):
        """ add header to teamplte,
            encode is true use make_header from email package """

    def addAlternative(template):
        """ add alternative mail template """

    def hasHeader(header):
        """ check header """

    def getHeaders():
        """ extra headers, (header_name, value, encode) """

    def addAttachment(file_data, content_type, filename):
        """ add attachment """

    def getAttachments():
        """ extra attachments, (file_data, content_type, filename, disposition) """

    def getAlternative():
        """ alternative """

    def update():
        """ update mailtemplate """

    def render():
        """ render mailtemplate and return results """

    def send(emails, **kw):
        """ generate email and send to emails, kw set as attributes """

    def __call__(**kw):
        """ update template and render, kw set as attributes """
