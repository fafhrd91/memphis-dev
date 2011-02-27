""" RichText field """
from zope import schema, interface
from zope.component import getUtility, queryUtility
from zope.schema.interfaces import WrongType, RequiredMissing

from memphis.schema.richtext.interfaces import \
    IRenderer, IRichText, IRichTextData


class RichText(schema.Text):
    interface.implements(IRichText)

    _type = None

    def __init__(self, default_format='source.plain', **kw):
        super(RichText, self).__init__(**kw)

        self.default_format = default_format

    def get(self, object):
        text = getattr(object, self.__name__, u'')
        format = getattr(object, '%s_format'%self.__name__, self.default_format)

        return RichTextData(text, format)

    def set(self, object, value):
        if self.readonly:
            raise TypeError("Can't set values on read-only fields "
                            "(name=%s, class=%s.%s)"
                            % (self.__name__,
                               object.__class__.__module__,
                               object.__class__.__name__))

        setattr(object, self.__name__, value.text)
        setattr(object, '%s_format'%self.__name__, value.format)

    def validate(self, value):
        if not isinstance(value, unicode):
            if not IRichTextData.providedBy(value):
                raise WrongType(value, IRichTextData)

            if self.required:
                if not value.text:
                    raise RequiredMissing()

        return super(RichText, self).validate(value)


class RichTextData(object):
    interface.implements(IRichTextData)

    def __init__(self, text=u'', format='source.plain'):
        self.format = format
        self.text = unicode(text)

    def render(self, request):
        renderer = queryUtility(IRenderer, name=self.format)
        if renderer is None:
            renderer = getUtility(IRenderer, name=u"source.plain")

        return renderer.render(request, self.text)

    def __len__(self):
        return len(self.text)

    def __nonzero__(self):
        return len(self.text) > 0

    def __eq__(self, other):
        if IRichTextData.providedBy(other):
            if (self.format == other.format) and (self.text == other.text):
                return True

        return False

    def __ne__(self, other):
        return not self.__eq__(other)
