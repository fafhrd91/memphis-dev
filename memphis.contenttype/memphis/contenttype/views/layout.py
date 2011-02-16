from zope import interface
from zope.component import getSiteManager

from memphis import view, config
from memphis.contenttype.interfaces import IContent, IDCDescriptive


# layout
class LayoutView(object):

    data = None
    title = None

    def update(self):
        super(LayoutView, self).update()

        dc = IDCDescriptive(self.maincontext, None)
        if dc is not None:
            self.title = dc.title
            self.description = dc.description


config.action(
    view.registerLayout,
    '', IContent, parent='page', klass = LayoutView,
    template=view.template("memphis.contenttype:templates/layout.pt"))
