"""

$Id: auth.py 11798 2011-01-31 04:14:24Z fafhrd91 $
"""
from zope import interface
from zope.component import getUtility

from pyramid import security
from pyramid.threadlocal import get_current_request

from memphis import storage, config
from memphis.users.interfaces import IUser, IUserInfo
from memphis.users.interfaces import IPasswordTool, IAuthentication


class User(storage.BehaviorBase):
    interface.implements(IUser)
    storage.behavior('memphis.user', schema=IUserInfo)


class Authentication(object):
    config.utility(IAuthentication)

    def authenticate(self, login, password):
        user = self.getUserByLogin(login)

        if user is not None:
            ds = IUserInfo(user)

            pwtool = getUtility(IPasswordTool)
            if pwtool.checkPassword(ds.password, password):
                return user

    def getUser(self, id):
        if id and id.startswith('memphis-'):
            try:
                user = storage.getItem(id[8:])
                user.id = id
                return user
            except:
                pass

    def getUserByLogin(self, login):
        sch = storage.getSchema(IUserInfo)

        ds = sch.query(sch.Type.login == login).first()
        if ds is not None:
            user = storage.getItem(ds.oid)
            user.id = 'memphis-%s'%user.oid
            return user

    def getCurrentUser(self):
        id = security.authenticated_userid(get_current_request())
        return self.getUser(id)
