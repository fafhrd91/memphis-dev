"""

$Id: validator.py 11798 2011-01-31 04:14:24Z fafhrd91 $
"""
from zope import interface, component, schema
from zope.component import getUtility

from memphis import config
from memphis.form import interfaces, validator

from memphis.users.interfaces import _

from interfaces import IPrincipalPasswordForm, IPersonalPasswordForm
from schemas import SPasswordForm, \
    CurrentPassword, PasswordFormError, CurrentPasswordError


class PasswordFormValidator(validator.InvariantsValidator):
    config.adapts(
        interface.Interface,
        interface.Interface,
        IPrincipalPasswordForm,
        interface.interfaces.IInterface,
        interface.Interface)

    def validate(self, data):
        if self.schema != SPasswordForm:
            return super(PasswordFormValidator, self).validate(data)

        password = self.view.widgets['password']
        cpassword = self.view.widgets['confirm_password']

        errors = []

        if password.error is None and cpassword.error is None:
            if data['password'] != data['confirm_password']:
                error = PasswordFormError()
                errors.append(error)

                view = component.getMultiAdapter(
                    (error, self.request, password, password.field,
                     self.view, self.context), interfaces.IErrorViewSnippet)
                view.update()
                password.error = view

                view = component.getMultiAdapter(
                    (error, self.request, cpassword, cpassword.field,
                     self.view, self.context), interfaces.IErrorViewSnippet)
                view.update()
                cpassword.error = view

        return tuple(errors) + super(PasswordFormValidator, self).validate(data)


class CurrentPasswordValidator(validator.SimpleFieldValidator):
    config.adapts(
        IPersonalPasswordForm,
        CurrentPassword)

    def validate(self, value):
        super(CurrentPasswordValidator, self).validate(value)

        # check current password
        if self.context.checkPassword(value):
            return

        raise CurrentPasswordError()
