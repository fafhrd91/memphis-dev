""" html renderer """
from zope import interface
from interfaces import _, IRenderer


class HTMLRenderer(object):
    interface.implements(IRenderer)

    title = _("HTML")
    description = _("HTML Source")

    def render(self, request, text):
        return text
