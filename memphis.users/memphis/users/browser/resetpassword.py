"""

$Id: resetpassword.py 4711 2011-02-02 22:55:35Z nikolay $
"""
from datetime import datetime
from pyramid import security
from webob.exc import HTTPFound

from zope import interface, schema
from zope.component import getUtility

from memphis import mail, view, config
from memphis.form import button, field, form

from memphis.users.interfaces import _
from memphis.users.interfaces import IPasswordTool, IAuthentication, IUserInfo
from memphis.users.exceptions import PasswordResetingError

from schemas import SPasswordForm
from interfaces import IPrincipalPasswordForm


class ResetPassword(object):

    def update(self):
        super(ResetPassword, self).update()

        request = self.request

        mailer = getUtility(mail.IMailer)
        self.from_name = mailer.email_from_name
        self.from_address = mailer.email_from_address

        if request.params.has_key('button.send'):
            login = request.params.get('login', '')

            principal = getUtility(IAuthentication).getUserByLogin(login)
            if principal is not None:
                passcode = getUtility(IPasswordTool).generatePasscode(principal)

                template = ResetPasswordTemplate(principal, request)
                template.passcode = passcode
                template.send()

                view.addMessage(
                    request,
                    _('Your password has been reset and is being emailed to you.'))
                raise HTTPFound(location=request.application_url)

            view.addMessage(
                request,
                _(u"System can't restore password for this principal."))


class ResetPasswordForm(form.Form):
    interface.implements(IPrincipalPasswordForm)

    ignoreContext = True
    fields = field.Fields(SPasswordForm)

    @property
    def label(self):
        return 'Password confirmation for %s'%self.info.fullname

    def update(self):
        request = self.request
        ptool = self.ptool = getUtility(IPasswordTool)

        passcode = request.params.get('passcode')
        principal = self.ptool.getPrincipal(passcode)
        self.info = IUserInfo(principal)

        if principal is not None:
            self.passcode = passcode
            self.principal = principal
        else:
            view.addMessage(request, _("Passcode is invalid."), 'warning')
            raise HTTPFound(
                location='%s/resetpassword.html'%request.application_url)

        super(ResetPasswordForm, self).update()

    @button.buttonAndHandler(_("Change password"))
    def changePassword(self, action):
        request = self.request
        data, errors = self.extractData()

        if errors:
            view.addMessage(request, self.formErrorsMessage, 'error')
        else:
            try:
                self.ptool.resetPassword(self.passcode, data['password'])
            except Exception, exc:
                view.addMessage(request, str(exc), 'warning')
                return

            user = getUtility(IAuthentication).getUserByLogin(self.info.login)
            headers = security.remember(request, user.id)

            view.addMessage(
                request, _('You have successfully changed your password.'))

            raise HTTPFound(
                headers = headers,
                location=request.application_url)


class ResetPasswordTemplate(mail.MailTemplate):

    subject = 'Password Reset Confirmation'
    template = view.template('memphis.users.browser:resetpasswordmail.pt')

    def update(self):
        super(ResetPasswordTemplate, self).update()

        request = self.request

        self.date = datetime.now()

        remoteAddr = request.get('REMOTE_ADDR', '')
        forwardedFor = request.get('HTTP_X_FORWARDED_FOR', None)

        self.from_ip = (forwardedFor and '%s/%s' %
                        (remoteAddr, forwardedFor) or remoteAddr)

        self.url = '%s/resetpasswordform.html?passcode=%s'%(
            request.application_url, self.passcode)

        info = IUserInfo(self.context)

        self.to_address = mail.formataddr((info.fullname, info.login))


config.action(
    view.registerView,
    'resetpassword.html', view.INavigationRoot,
    klass = ResetPassword,
    template = view.template('memphis.users.browser:resetpassword.pt'))

config.action(
    view.registerView,
    'resetpasswordform.html', view.INavigationRoot,
    klass = ResetPasswordForm)
