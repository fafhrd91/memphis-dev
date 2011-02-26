""" Plain Text Renderer """
import cgi
from zope import interface
from memphis import config
from interfaces import _, IRenderer


class PlainTextRenderer(object):
    """
    >>> renderer = PlainTextRenderer()

    >>> print renderer.render('Test text1\\n   test text2\\n test text3   ')
    Test text1<br />
    &nbsp;&nbsp;&nbsp;test text2<br />
    &nbsp;test text3
    """
    interface.implements(IRenderer)
    config.utility(IRenderer, name='source.plain')

    title = _("Plain Text")
    description = _("Formatted plain Text Source")

    def render(self, request, text):
        lines = []
        for line in cgi.escape(text).split('\n'):
            l = u''
            idx = 0
            for ch in line:
                if ch == u' ':
                    idx += 1
                    l = l + u'&nbsp;'
                else:
                    break

            lines.append(l + line[idx:] + u'<br />')

        if lines:
            lines[-1] = lines[-1][:-6]

        return u'\n'.join(lines)
