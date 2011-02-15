# memphis.mail public API

# mailer
from memphis.mail.interfaces import IMailer

# public api for templates
from email.Utils import formatdate, formataddr
from memphis.mail.template import MailTemplate
