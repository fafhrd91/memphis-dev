"""

$Id: fields.py 11798 2011-01-31 04:14:24Z fafhrd91 $
"""
from zope import interface, schema
from zope.component import getUtility, queryUtility
from z3c.schema.email import RFC822MailAddress

from exceptions import LoginInUse
from interfaces import ILoginField, INewLoginField
from interfaces import IAuthentication, IPassword, IPasswordTool


class Password(schema.Password):
    interface.implements(IPassword)

    def validate(self, value):
        super(Password, self).validate(value)

        ptool = queryUtility(IPasswordTool)
        if ptool is not None:
            ptool.validatePassword(value)


class LoginField(RFC822MailAddress):
    interface.implements(ILoginField)

    def set(self, context, value):
        """ lower login before set """
        if value:
            value = value.lower()
        super(LoginField, self).set(context, value)

    def validate(self, value):
        super(LoginField, self).validate(value)

        if self.context is None:
            return

        login = value.lower()
        oldlogin = self.query(self.context)

        if login != oldlogin:
            if getUtility(IAuthentication).getUser(value) is not None:
                raise LoginInUse()


class NewLoginField(LoginField):
    interface.implements(INewLoginField)

    def validate(self, value):
        super(NewLoginField, self).validate(value)

        if getUtility(IAuthentication).getUser(value) is not None:
            raise LoginInUse()
