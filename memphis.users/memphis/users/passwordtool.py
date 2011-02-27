"""

$Id: passwordtool.py 11798 2011-01-31 04:14:24Z fafhrd91 $
"""
from os import urandom
from random import randint
from codecs import getencoder
from hashlib import md5, sha1
from base64 import urlsafe_b64encode
from base64 import urlsafe_b64decode

from zope import interface
from zope.component import getUtility, queryUtility

from memphis import config, controlpanel, storage
from memphis.users import utils, exceptions
from memphis.users.interfaces import _, IPasswordTool, IPasswordReset, IUserInfo
from memphis.users.exceptions import PasswordResetingError

_encoder = getencoder("utf-8")


class SSHAPasswordManager(object):
    """SSHA password manager.

    SSHA is basically SHA1-encoding which also incorporates a salt
    into the encoded string. This way, stored passwords are more
    robust against dictionary attacks of attackers that could get
    access to lists of encoded passwords.

    SSHA is regularly used in LDAP databases and we should be
    compatible with passwords used there.

    >>> from zope.interface.verify import verifyObject

    >>> manager = SSHAPasswordManager()
    >>> verifyObject(IPasswordManager, manager)
    True

    >>> password = u"right \N{CYRILLIC CAPITAL LETTER A}"
    >>> encoded = manager.encodePassword(password, salt="")
    >>> encoded
    '{SSHA}BLTuxxVMXzouxtKVb7gLgNxzdAI='

    >>> manager.checkPassword(encoded, password)
    True
    >>> manager.checkPassword(encoded, password + u"wrong")
    False

    Using the `slappasswd` utility to encode ``secret``, we get
    ``{SSHA}J4mrr3NQHXzLVaT0h9TuEWoJOrxeQ5lv`` as seeded hash.

    Our password manager generates the same value when seeded with the
    same salt, so we can be sure, our output is compatible with
    standard LDAP tools that also use SSHA::

    >>> from base64 import urlsafe_b64decode
    >>> salt = urlsafe_b64decode('XkOZbw==')
    >>> encoded = manager.encodePassword('secret', salt)
    >>> encoded
    '{SSHA}J4mrr3NQHXzLVaT0h9TuEWoJOrxeQ5lv'

    >>> encoded = manager.encodePassword(password)
    >>> manager.checkPassword(encoded, password)
    True
    >>> manager.checkPassword(encoded, password + u"wrong")
    False

    >>> manager.encodePassword(password) != manager.encodePassword(password)
    True

    The password manager should be able to cope with unicode strings for input::

    >>> passwd = u'foobar\u2211' # sigma-sign.
    >>> manager.checkPassword(manager.encodePassword(passwd), passwd)
    True
    >>> manager.checkPassword(unicode(manager.encodePassword(passwd)), passwd)
    True

    """
    def encodePassword(self, password, salt=None):
        if salt is None:
            salt = urandom(4)
        hash = sha1(_encoder(password)[0])
        hash.update(salt)
        return '{SSHA}' + urlsafe_b64encode(hash.digest() + salt)

    def checkPassword(self, encoded_password, password):
        # urlsafe_b64decode() cannot handle unicode input string. We
        # encode to ascii. This is safe as the encoded_password string
        # should not contain non-ascii characters anyway.
        encoded_password = encoded_password.encode('ascii')
        byte_string = urlsafe_b64decode(encoded_password[6:])
        salt = byte_string[20:]
        return encoded_password == self.encodePassword(password, salt)


class PasswordTool(object):
    interface.implements(IPasswordTool)

    passwordManager = SSHAPasswordManager()

    def checkPassword(self, encodedPassword, password):
        return self.passwordManager.checkPassword(encodedPassword, password)

    def encodePassword(self, password, salt=None):
        return self.passwordManager.encodePassword(password, salt)

    def getPrincipal(self, passcode):
        sch = storage.getSchema(IPasswordReset)

        rec = sch.query(sch.Type.passcode == passcode).first()
        if rec is not None:
            return storage.getItem(rec.oid)

    def generatePasscode(self, principal):
        principal.applySchema(IPasswordReset)

        passcode = utils.genPassword2(32)
        IPasswordReset(principal).passcode = passcode
        return passcode

    def resetPassword(self, passcode, password):
        principal = self.getPrincipal(passcode)
        if principal is None:
            raise PasswordResetingError("Passcode is invalid")

        IUserInfo(principal).password = self.encodePassword(password)
        principal.removeSchema(IPasswordReset)

    def validatePassword(self, password):
        """
    >>> import zope.interface.verify
    >>> from zope import interface, component

    >>> zope.interface.verify.verifyClass(
    ...     interfaces.IPasswordChecker, DefaultPasswordChecker)
    True

    Default password checker uses IDefaultPasswordChecker utility
    to get configuration. We use controlpanel configlet for this but
    in this code we should create it.

    >>> checker = default.DefaultPasswordChecker()
    >>> checker.min_length = 5
    >>> checker.letters_digits = False
    >>> checker.letters_mixed_case = False

    >>> zope.interface.verify.verifyObject(IPasswordChecker, checker)
    True

    >>> checker.validate('passw')

    >>> checker.validate('ps1')
    Traceback (most recent call last):
    ...
    LengthPasswordError: ...

    >>> configlet.min_length = 6
    >>> checker.validate('passw')
    Traceback (most recent call last):
    ...
    LengthPasswordError: ...

    >>> checker.validate('password')

    >>> configlet.letters_digits = True

    >>> checker.validate('password')
    Traceback (most recent call last):
    ...
    LettersDigitsPasswordError

    >>> checker.validate('66665555')
    Traceback (most recent call last):
    ...
    LettersDigitsPasswordError

    >>> checker.validate('pass5word')

    >>> configlet.letters_mixed_case = True
    >>> checker.validate('pass5word')
    Traceback (most recent call last):
    ...
    LettersCasePasswordError

    >>> checker.validate('PASS5WORD')
    Traceback (most recent call last):
    ...
    LettersCasePasswordError

    >>> checker.validate('Pass5word')

    By default password strength is always 100%

    >>> checker.passwordStrength('Pass5word')
    100.0

        """
        if len(password) < self.min_length:
            raise exceptions.LengthPasswordError(
                _('Password should be at least ${count} characters.',
                  mapping={'count': self.min_length}))
        elif self.letters_digits and \
                 (password.isalpha() or password.isdigit()):
            raise exceptions.LettersDigitsPasswordError()
        elif self.letters_mixed_case and \
                 (password.isupper() or password.islower()):
            raise exceptions.LettersCasePasswordError()

    def passwordStrength(self, password):
        return 100.0


controlpanel.registerConfiglet(
    'principals.password', IPasswordTool, PasswordTool,
    _("Password tool"), _("Password managing/generating configuration."))
