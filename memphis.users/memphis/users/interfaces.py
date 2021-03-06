"""

$Id: interfaces.py 11798 2011-01-31 04:14:24Z fafhrd91 $
"""
from zope import interface, schema
from pyramid.i18n import TranslationStringFactory
from memphis import storage

MessageFactory = _ = TranslationStringFactory('memphis.users')


class IAuthentication(interface.Interface):
    """ authentication service """

    def isAnonymous():
        """ check if current use is anonymous """

    def authenticate(credentials):
        """ authenticate credentials """

    def getUserByLogin(login):
        """ return user by login """


class IUser(interface.Interface):
    """ user behavior """


class IUserInfo(interface.Interface):
    storage.schema('memphis.user:info')

    fullname = schema.TextLine(
        title = u'Fullname',
        required = True)

    login = schema.TextLine(
        title = u'Login',
        required = True)

    password = schema.TextLine(
        title = u'Password',
        required = True)

    confirmed = schema.Bool(
        title = u'Confirmed',
        required = False)


# memphis.users fields
class ILoginField(schema.interfaces.IText):
    """ principal login field """


class INewLoginField(ILoginField):
    """ new login field """


# password support
class IPassword(schema.interfaces.IPassword):
    """ password field """


class IPasswordTool(interface.Interface):
    """ password tool """

    min_length = schema.Int(
        title = _(u'Minimum length'),
        description = _(u'Minimun length of password.'),
        default = 5,
        required = True)

    letters_digits = schema.Bool(
        title = _(u'Letters and digits'),
        description = _(u'Password should contain both letters and digits.'),
        default = False,
        required = True)

    letters_mixed_case = schema.Bool(
        title = _(u'Letters case'),
        description = _(u'Password should contain letters in mixed case.'),
        default = False,
        required = True)

    def encodePassword(password, *args, **kw):
        """ encode password """

    def checkPassword(encodedPassword, password):
        """ check password """

    def validatePassword(password):
        """ validate password """

    def passwordStrength(password):
        """ check password strength """

    def getPasscode(pid):
        """ return passcode by principal """

    def getPrincipal(passcode):
        """ return principal by passcode """

    def generatePasscode(principal):
        """ generate passcode for principal """

    def resetPassword(passcode, password):
        """ reset password """


class IPasswordReset(interface.Interface):
    storage.schema('memphis.user:resetpassword')

    passcode = schema.TextLine(
        title = u'Reset password code',
        required = True)


class IPasswordPreference(interface.Interface):
    """ password preference """


# ttw profile
class IUserProfileConfiglet(interface.Interface):
    """ ttw profile configlet """

    upschema = schema.Choice(
        title = u'User profile schema',
        vocabulary = 'memphis.ttw-schemas',
        required = False)


# site registration
class ISiteRegistration(interface.Interface):
    """ registration settings """

    public = schema.Bool(
        title = u'Public',
        description = u'Member registration is public.',
        required = False,
        default = True)

    invitation = schema.Bool(
        title = u'Invitation',
        description = u'Use invitation system for member registration.',
        required = False,
        default = False)

    emailauth = schema.Bool(
        title = u'Authorization',
        description = u'Enable email member authorization.',
        required = False,
        default = False)


class IRegistrationForm(interface.Interface):
    """ registration form """

    principal = interface.Attribute('Principal object')

    def create(data):
        """ create principal """

    def setPrincipal(principal):
        """ set newly created principal """
