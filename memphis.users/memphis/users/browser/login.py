"""

$Id: login.py 11798 2011-01-31 04:14:24Z fafhrd91 $
"""
from urllib import quote, unquote

from zope import interface
from zope.component import getUtility

from pyramid import security
from webob.exc import HTTPFound

from memphis import config, view
from memphis.form import form, field, button
from memphis.users.interfaces import _, IUserInfo, IAuthentication

from schemas import SLoginForm


class LoginForm(form.Form):

    title = _('Login')

    ignoreContext = True
    fields = field.Fields(SLoginForm)

    @button.buttonAndHandler(_(u"Log in"))
    def handleLogin(self, action):
        request = self.request

        data, errors = self.extractData()
        if errors:
            #IStatusMessage(request).add(self.formErrorsMessage, 'error')
            self.status = self.formErrorsMessage
            return

        user = getUtility(IAuthentication).authenticate(
            data['login'], data['password'])

        if user is not None:
            headers = security.remember(request, user.id)

            #print '========================================', user.id
            #print headers
            raise HTTPFound(
                headers = headers,
                location = '%s/login-success.html'%request.application_url)

        self.status = "You enter wrong login or password."

    def update(self):
        super(LoginForm, self).update()

        request = self.request
        self.portalURL = request.application_url
        self.loginURL = '%s/login.html'%self.portalURL

        auth = getUtility(IAuthentication)

        #print auth.getCurrentUser()
        #print security.authenticated_userid(self.request)

        if auth.getCurrentUser() is not None:
            raise HTTPFound(location = '%s/login-success.html'%self.portalURL)


class LoginSuccess(object):

    def update(self):
        auth = getUtility(IAuthentication)

        user = auth.getCurrentUser()
        if user is None:
            raise HTTPFound(
                location = '%s/login.html'%self.request.application_url)
        else:
            self.user = IUserInfo(user)


class LogoutForm(object):

    def update(self):
        request = self.request
        uid = security.authenticated_userid(request)

        if uid is not None:
            headers = security.forget(request)
            raise HTTPFound(
                headers = headers,
                location = '%s/logout.html'%request.application_url)


config.action(
    view.registerView,
    'login.html', view.IRoot,
    klass = LoginForm,
    template=view.template("memphis.users.browser:login.pt"))

config.action(
    view.registerView,
    'login-success.html', view.IRoot,
    klass = LoginSuccess,
    template=view.template("memphis.users:browser/login-success.pt"))

config.action(
    view.registerView,
    'logout.html', view.IRoot,
    klass = LogoutForm,
    template=view.template("logout.pt"))
