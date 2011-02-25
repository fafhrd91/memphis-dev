""" RichText field interfaces """
from zope import schema, interface
from zope.schema.interfaces import IField
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('memphis.schema')


class IRichText(IField):
    """ rich text field """

    default_format = schema.Choice(
        title = u'Default format',
        default = u"source.plaintext",
        vocabulary = u'richtext-renderers',
        required = False)


class IRichTextDataModified(IObjectEvent):

    data = interface.Attribute('IRichTextData object')


class IRichTextWidget(interface.Interface):
    """ rich text widget """


class IRenderer(interface.Interface):
    """ renderer """

    title = interface.Attribute('Title')

    description = interface.Attribute('Description')

    def render(text):
        """ render source text to html """
