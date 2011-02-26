""" html renderer """
from zope import interface
from memphis import config

from interfaces import _, IRenderer


class HTMLRenderer(object):
    interface.implements(IRenderer)
    config.utility(IRenderer, name='source.html')

    title = _("HTML")
    description = _("HTML Source")

    def render(self, request, text):
        return text
