""" change password form

$Id: password.py 4662 2011-02-01 07:31:15Z nikolay $
"""
from zope import interface

from memphis import config, view
from memphis.form import form, field, button
from memphis.users.interfaces import _, IUserInfo, IPasswordPreference

from schemas import SChangePasswordForm, SPasswordForm
from interfaces import IPrincipalPasswordForm, IPersonalPasswordForm


class PrincipalPassword(form.EditForm):
    """ change password form """
    interface.implements(IPrincipalPasswordForm, IPersonalPasswordForm)

    ignoreContext = True

    label = _('Change password')
    fields = field.Fields(SChangePasswordForm, SPasswordForm)

    def update(self, *args, **kw):
        principal = self.context.user

        info = IUserInfo(principal)

        self.principal_login = info.login
        self.principal_title = info.fullname
        return super(PrincipalPassword, self).update()

    @button.buttonAndHandler(_(u"Change password"))
    def applyChanges(self, action):
        #service = IStatusMessage(self.request)

        data, errors = self.extractData()
        if errors:
            #service.add(self.formErrorsMessage, 'error')
            self.status = self.formErrorsMessage

        elif data['password']:
            self.context.changePassword(data['password'])
            #service.add(_('Password has been changed for ${title}.',
            #              mapping = {'title': self.principal_title}))

            self.status = _('Password has been changed for ${title}.',
                            mapping = {'title': self.principal_title})


config.action(
    view.registerView,
    'index.html', IPasswordPreference,
    klass=PrincipalPassword)
