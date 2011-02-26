""" default RichText widget """
from zope import schema, component, interface
from zope.component import getUtility, queryUtility, getMultiAdapter

from memphis import form, config, view
from memphis.form import interfaces
from memphis.form.browser import textarea

from interfaces import _
from interfaces import IRichText, IRichTextData

import vocabulary
from field import RichTextData


class RichTextWidget(textarea.TextAreaWidget):
    config.adapts(IRichText, None)
    config.adapts(IRichText, None, name='richtext-simple')

    rows = 15
    klass = 'widget-richtext'

    __fname__ = 'richtext'
    __title__ = _(u'Basic HTML textarea')
    __description__ = _(u'HTML Text Area input widget')

    def update(self):
        field = self.field

        self.format = schema.Choice(
            __name__ = '%s_format'%field.__name__,
            title = _(u"Text format"),
            description = _(u"If you are unsure of which format to use, just select Plain Text and type the document as you usually do."),
            vocabulary = vocabulary.getRenderers(),
            default = 'source.plain',
            required = False)

        self.format.context = self

        self.format_widget = getMultiAdapter(
            (self.format, self.request),  form.IDefaultWidget)
        self.format_widget.mode = self.mode
        self.format_widget.context = self
        self.format_widget.update()

        super(RichTextWidget, self).update()

    def extract(self, default=interfaces.NO_VALUE):
        textarea = self.request.params.get(self.name, default)
        format = self.format_widget.extract()

        if textarea is default and format is default:
            return default

        if format is not default:
            format = format[0]

        return RichTextData(textarea, format)

    def getValue(self):
        if IRichTextData.providedBy(self.value):
            return self.value.text
        else:
            return self.value


class DataConverter(object):
    config.adapts(IRichText, RichTextWidget)
    interface.implements(form.IDataConverter)

    def __init__(self, field, widget):
        self.field = field
        self.widget = widget

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return RichTextData(u'', self.widget.field.default_format)
        return value

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        return value


config.action(
    view.registerPagelet,
    form.IWidgetDisplayView, RichTextWidget,
    template=view.template("memphis.schema.richtext:widget_display.pt"))

config.action(
    view.registerPagelet,
    form.IWidgetInputView, RichTextWidget,
    template=view.template("memphis.schema.richtext:widget_input.pt"))

config.action(
    view.registerPagelet,
    form.IWidgetHiddenView, RichTextWidget,
    template=view.template("memphis.schema.richtext:widget_hidden.pt"))
