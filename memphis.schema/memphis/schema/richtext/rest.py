""" ReStructured Text renderer """
import docutils.core
from docutils.writers.html4css1 import Writer
from docutils.writers.html4css1 import HTMLTranslator

from zope import interface
from interfaces import _, IRenderer


class Translator(HTMLTranslator):

    def astext(self):
        # use the title, subtitle, author, date, etc., plus the content
        body = self.body_pre_docinfo + self.docinfo + self.body
        return u"".join(body)


class ReStructuredTextRenderer(object):
    interface.implements(IRenderer)

    title = _("ReStructured Text (ReST)")
    description = _("ReStructured Text (ReST) Source")

    def render(self, request, text, settings_overrides={}):
        overrides = {
            'halt_level': 6,
            'input_encoding': 'unicode',
            'output_encoding': 'unicode',
            'initial_header_level': 3,
            }
        overrides.update(settings_overrides)
        writer = Writer()
        writer.translator_class = Translator
        html = docutils.core.publish_string(
            text,
            writer=writer,
            settings_overrides=overrides,
            )
        return html
