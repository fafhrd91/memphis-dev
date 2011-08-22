from zope.component import getUtility

from memphis import config, view
from memphis.users.interfaces import IAuthentication

view.static('testapp', 'testapp:static')


view.registerLayout(
    'page', context=view.INavigationRoot,
    template = view.template("testapp:templates/layoutpage.pt"))


class LayoutWorkspace(view.Layout):
    view.layout('workspace', view.INavigationRoot, parent="page")

    template=view.template("testapp:templates/layoutworkspace.pt")

    def update(self):
        self.user = getUtility(IAuthentication).getCurrentUser()
        self.isAnon = self.user is None


view.registerView(
    'index.html', view.INavigationRoot, default=True,
    template=view.template("testapp:templates/welcome.pt"))


view.registerLayout(
    '', view.INavigationRoot, parent="workspace",
    template=view.template("testapp:templates/layoutcontent.pt"))
