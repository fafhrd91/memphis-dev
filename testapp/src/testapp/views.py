from zope import component
from memphis import config, view, storage
from memphis.users.interfaces import IUserInfo, IAuthentication


class LayoutPage(object):

    def update(self):
        user = component.getUtility(IAuthentication).getCurrentUser()

        self.user = None
        self.userId = getattr(user, 'id', None)
        self.isAnon = self.userId is None

        if self.userId is not None:
            self.user = user.getDatasheet(IUserInfo)


view.registerLayout(
    'page', context=view.IRoot,
    klass = LayoutPage,
    template=view.template("testapp:templates/layoutpage.pt"))

view.registerLayout(
    parent='page', context=view.IRoot,
    template=view.template("testapp:templates/layoutcontent.pt"))

view.registerView(
    'index.html', view.IRoot,
    template=view.template("testapp:templates/welcome.pt"))

view.registerDefaultView(
    'index.html', view.IRoot)
