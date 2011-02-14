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
            self.user = IUserInfo(user)


view.registerLayout(
    'page', context=view.INavigationRoot,
    klass = LayoutPage,
    template=view.template("testapp:templates/layoutpage.pt"))

view.registerLayout(
    parent='page', context=view.INavigationRoot,
    template=view.template("testapp:templates/layoutcontent.pt"))

view.registerView(
    'index.html', view.INavigationRoot,
    template=view.template("testapp:templates/welcome.pt"))

view.registerDefaultView(
    'listing.html', view.INavigationRoot)
