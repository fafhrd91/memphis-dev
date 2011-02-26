""" RichText field interfaces """
from zope import schema, interface
from zope.schema.interfaces import IField
from zope.component.interfaces import IObjectEvent
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('memphis.schema')


class IRichText(IField):
    """ rich text field """

    default_format = schema.Choice(
        title = u'Default format',
        default = "source.plain",
        #vocabulary = u'richtext-renderers',
        values = ["source.plain"],
        required = True)


class IRichTextData(interface.Interface):

    text = interface.Attribute('Text')
    format = interface.Attribute('Format')


class IRichTextWidget(interface.Interface):
    """ rich text widget """


class IRenderer(interface.Interface):
    """ renderer """

    title = interface.Attribute('Title')

    description = interface.Attribute('Description')

    def render(request, text):
        """ render source text to html """
