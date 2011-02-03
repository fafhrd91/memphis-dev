"""

$Id: schemas.py 4669 2011-02-01 08:20:09Z nikolay $
"""
from zope import schema, interface
from memphis.users.fields import Password, NewLoginField
from memphis.users.interfaces import _


class PasswordFormError(schema.ValidationError):
    __doc__ = _("Password and Confirm Password should be the same.")


class CurrentPasswordError(schema.ValidationError):
    __doc__ = _(u'Does not match current password.')


class CurrentPassword(schema.Password):
    """ field for checking current password """


class SRegistrationForm(interface.Interface):

    firstname = schema.TextLine(
        title=_('First Name'),
        description=_(u"e.g. John. This is how users "
                      u"on the site will identify you."),
        required = True)

    lastname = schema.TextLine(
        title=_('Last Name'),
        description=_(u"e.g. Smith. This is how users "
                      u"on the site will identify you."),
        required = True)

    login = NewLoginField(
        title = _(u'E-mail/Login'),
        description = _(u'This is the username you will use to log in. '\
            'It must be an email address. <br /> Your email address will not '\
            'be displayed to any user or be shared with anyone else.'),
        required = True)


class SLoginForm(interface.Interface):
    """ login form """

    login = schema.TextLine(
        title = _(u'Login Name'),
        description = _('Login names are case sensitive, '\
                            'make sure the caps lock key is not enabled.'),
        required = True)

    password = schema.Password(
        title = _(u'Password'),
        description = _('Case sensitive, make sure caps lock is not enabled.'),
        required = True)


class SPasswordForm(interface.Interface):

    password = Password(
        title = _(u'New password'),
        description = _(u'Enter new password. '\
                        u'No spaces or special characters, should contain '\
                        u'digits and letters in mixed case.'),
        default = u'',
        required = True)

    confirm_password = Password(
        title = _(u'Confirm password'),
        description = _(u'Re-enter the password. '
                        u'Make sure the passwords are identical.'),
        missing_value = u'',
        required = True)


class SChangePasswordForm(interface.Interface):

    current_password = CurrentPassword(
        title = _(u'Current password'),
        description = _(u'Enter your current password.'),
        missing_value = u'',
        required = True)
