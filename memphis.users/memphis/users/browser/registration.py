"""

$Id: registration.py 11798 2011-01-31 04:14:24Z fafhrd91 $
"""
from zope import event, interface
from zope.component import getUtility
from zope.lifecycleevent import ObjectCreatedEvent

from pyramid import security
from webob.exc import HTTPFound

from memphis import config, view, storage
from memphis.form import form, field, button
from memphis.users.interfaces import \
    _, IUser, IUserInfo, IPasswordTool, IAuthentication, IRegistrationForm

from interfaces import IPrincipalPasswordForm
from schemas import SRegistrationForm, SPasswordForm


class Registration(form.EditForm):
    interface.implements(IRegistrationForm, IPrincipalPasswordForm)

    label = _("Registration form")

    ignoreContext = True
    fields = field.Fields(SRegistrationForm,
                          SPasswordForm).omit('confirmed')

    principal = None

    def getContent(self):
        return self.principal

    def create(self, data):
        # create user
        item = storage.insertItem('memphis.user')

        datasheet = IUserInfo(item)
        datasheet.login = data['login']
        datasheet.fullname = u'%s %s'%(data['firstname'], data['lastname'])
        datasheet.confirmed = True

        # set password
        passwordtool = getUtility(IPasswordTool)
        datasheet.password = passwordtool.encodePassword(data['password'])

        event.notify(ObjectCreatedEvent(item))
        return item

    def setPrincipal(self, principal):
        self.principal = principal

    @button.buttonAndHandler(_(u"Register"))
    def handle_register(self, action):
        request = self.request

        data, errors = self.extractData()
        if errors:
            view.addMessage(request, self.formErrorsMessage, 'error')
            return

        self.setPrincipal(self.create(data))

        user = getUtility(IAuthentication).getUserByLogin(data['login'])
        headers = security.remember(request, user.id)

        raise HTTPFound(
            location='%s/login-success.html'%request.application_url,
            headers = headers)


config.action(
    view.registerView,
    'join.html', view.INavigationRoot, klass=Registration)
