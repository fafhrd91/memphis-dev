""" default content view """
from zope import interface
from zope.dublincore.interfaces import IDCDescriptiveProperties

from memphis import form, view
from memphis.content.interfaces import IContent
from memphis.content.browser import CheckTypePermission
from memphis.content.browser.edit import EditContent


class ViewContent(form.DisplayForm, EditContent):
    view.zopeView('index.html', IContent,
                  default = True,
                  decorator = CheckTypePermission)

    label = ''
    description = ''

    def update(self):
        self.dc = dc = IDCDescriptiveProperties(self.context)
        self.description = dc.description

        super(ViewContent, self).update()
