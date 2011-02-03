"""

$Id: exceptions.py 11778 2011-01-30 07:42:47Z fafhrd91 $
"""
from zope import schema
from memphis.users.interfaces import _


class LoginInUse(schema.ValidationError):
    __doc__ = u'Login name already in use.'


class InvalidPascode(schema.ValidationError):
    """ Passcode is Invalide """


class PasswordError(schema.ValidationError):
    """ password validation error """


class PasswordResetingError(schema.ValidationError):
    """ Can't reset password """


class LengthPasswordError(PasswordError):
    __doc__ = _('Password min length exceeded.')

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return str(self.message)

    def doc(self):
        return self.message


class LettersDigitsPasswordError(PasswordError):
    __doc__ = _('Password should contain both letters and digits.')


class LettersCasePasswordError(PasswordError):
    __doc__ = _('Password should contain letters in mixed case.')
