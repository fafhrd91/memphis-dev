"""

$Id: preferences.py 4669 2011-02-01 08:20:09Z nikolay $
"""
from zope import interface
from zope.component import getUtility
from memphis import storage, config, preferences

from interfaces import _
from interfaces import IAuthentication, IUserInfo
from interfaces import IPasswordTool, IPasswordPreference


class PasswordPreference(object):
    interface.implements(IPasswordPreference)

    def __bind__(self, principal):
        clone = super(PasswordPreference, self).__bind__(principal)

        clone.user = getUtility(IAuthentication).getUser(principal.id)
        clone.ptool = getUtility(IPasswordTool)
        #clone.changer = IPasswordChanger(clone.__principal__, None)
        return clone

    def checkPassword(self, password):
        return self.ptool.checkPassword(
            IUserInfo(self.user).password, password)

    def changePassword(self, password):
        IUserInfo(self.user).password = \
            passwordTool.encodePassword(password)

    def isAvailable(self):
        if self.user is None:
            return False
        else:
            return super(PasswordPreference, self).isAvailable()


config.action(
    preferences.registerPreference,
    'membership.password', IPasswordPreference,
    klass = PasswordPreference,
    title = _('Change password'),
    description = _('You can change your password here.'))
