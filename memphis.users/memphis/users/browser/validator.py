""" custom validators """
from zope import interface
from memphis import config, form
from memphis.users.interfaces import _

from interfaces import IPrincipalPasswordForm, IPersonalPasswordForm
from schemas import CurrentPassword, PasswordFormError, CurrentPasswordError


class PasswordFormValidator(object):
    config.adapts(IPrincipalPasswordForm, name='password.validation')
    interface.implements(form.IFormValidator)

    def __init__(self, form):
        self.form = form

    def validate(self, data):
        password = self.form.widgets['password']
        cpassword = self.form.widgets['confirm_password']

        errors = []

        if password.error is None and cpassword.error is None:
            if data['password'] != data['confirm_password']:
                error = PasswordFormError()
                errors.append(form.WidgetError('password', error))
                errors.append(form.WidgetError('confirm_password', error))

        return errors


class CurrentPasswordValidator(form.FieldValidator):
    config.adapts(
        IPersonalPasswordForm,
        CurrentPassword)

    def validate(self, value):
        super(CurrentPasswordValidator, self).validate(value)

        # check current password
        if self.form.context.checkPassword(value):
            return

        raise CurrentPasswordError()
