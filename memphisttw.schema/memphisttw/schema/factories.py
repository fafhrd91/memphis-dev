from zope import interface, component, schema
from zope.interface.interface import InterfaceClass
from zope.schema import interfaces as schema_interfaces
from z3c.schema.email.interfaces import IRFC822MailAddress
from z3c.schema.baseurl.interfaces import IBaseURL

from memphis import config
from memphis.schema import RichText
from memphis.schema.richtext.interfaces import IRichText
from memphisttw.schema.interfaces import \
    _, ISchema, IChoice, IChoiceList,IFieldFactory
from memphisttw.schema.fields import Choice, ChoiceList, List, URL, EMail


class FieldFactory(object):
    interface.implements(IFieldFactory)

    hiddenFields = ()
    skipFields = ('readonly', 'order')
    mapToField = ('default', 'missing_value')
    mapToTextline = ()

    def __init__(self, name, field, schema, 
                 title='', description='', hiddenFields=()):
        self.name = name
        self.field = field
        self.title = title
        self.description = description
        self.field.__factory__ = self

        self.schema = self.wrapSchema(schema, field, hiddenFields)

    def __call__(self, **kw):
        return self.field(**kw)

    def mapField(self, name, field):
        mapField = None
        if field.__class__ == schema.Field:
            if name in self.mapToField:
                mapField = self.field
            elif name in self.mapToTextline:
                mapField = TextLine
        return mapField

    def wrapSchema(self, sch, field, hfields):
        wschema = InterfaceClass(sch.__name__, (interface.Interface,),
                                 __doc__ = sch.__doc__,
                                 __module__ = 'memphisttw.schema.schemas')

        for name, fld in schema.getFieldsInOrder(sch):
            if name in self.skipFields or name in hfields:
                continue

            mfield = self.mapField(name, fld)
            if mfield is not None:
                fld = mfield(
                    __name__ = name,
                    title = fld.title,
                    description = fld.description,
                    required = False)

            if fld.__class__ == schema.Field:
                continue

            wschema._InterfaceClass__attrs[name] = fld

        return wschema

    @interface.implementer(IFieldFactory)
    def getFactory(self, *args):
        return self


# Boolean
Bool = FieldFactory(
    'boolean', schema.Bool, schema.interfaces.IBool,
    title = _("Boolean"),
    description = _("Boolean field (YES or NO)."))

config.action(
    config.registerAdapter, Bool.getFactory, (ISchema,), name=Bool.name)

config.action(
    config.registerAdapter, Bool.getFactory, (schema.interfaces.IBool,))


# Integer
Int = FieldFactory(
    'int', schema.Int, schema.interfaces.IInt,
    title = _("Integer"),
    description = _("Field containing an Integer Value."))

config.action(
    config.registerAdapter, Int.getFactory, (ISchema,), name=Int.name)

config.action(
    config.registerAdapter, Int.getFactory, (schema.interfaces.IInt,))


# Text
Text = FieldFactory(
    'text', schema.Text, schema.interfaces.IText,
    title = _("Text"),
    description = _("Field containing text with newlines."))

config.action(
    config.registerAdapter, Text.getFactory, (ISchema,), name=Text.name)

config.action(
    config.registerAdapter, Text.getFactory, (schema.interfaces.IText,))


# Text Line
TextLine = FieldFactory(
    'textline', schema.TextLine, schema.interfaces.ITextLine,
    title = _("Text Line"),
    description = _("Field containing text line without newlines."))

config.action(
    config.registerAdapter, TextLine.getFactory, (ISchema,), name=TextLine.name)

config.action(
    config.registerAdapter, TextLine.getFactory, (schema.interfaces.ITextLine,))


# Float
Float = FieldFactory(
    'float', schema.Float, schema.interfaces.IFloat,
    title = _("Float"),
    description = _("Field containing a Float."))

config.action(
    config.registerAdapter, Float.getFactory, (ISchema,), name=Float.name)

config.action(
    config.registerAdapter, Float.getFactory, (schema.interfaces.IFloat,))


# Decimal
Decimal = FieldFactory(
    'decimal', schema.Decimal, schema.interfaces.IDecimal,
    title = _("Decimal"),
    description = _("Field containing a Dicmal."))

config.action(
    config.registerAdapter, Decimal.getFactory, (ISchema,), name=Decimal.name)

config.action(
    config.registerAdapter, Decimal.getFactory, (schema.interfaces.IDecimal,))


# Date
Date = FieldFactory(
    'date', schema.Date, schema.interfaces.IDate,
    title = _("Date"),
    description = _("Field containing a date."))

config.action(
    config.registerAdapter, Date.getFactory, (ISchema,), name=Date.name)

config.action(
    config.registerAdapter, Date.getFactory, (schema.interfaces.IDate,))


# Datetime
Datetime = FieldFactory(
    'datetime', schema.Datetime, schema.interfaces.IDatetime,
    title = _("DateTime"),
    description = _("Field containing a DateTime."))

config.action(
    config.registerAdapter, Datetime.getFactory, (ISchema,), name=Datetime.name)

config.action(
    config.registerAdapter, Datetime.getFactory, (schema.interfaces.IDatetime,))


# Time
Time = FieldFactory(
    'time', schema.Time, schema.interfaces.ITime,
    title = _("Time"),
    description = _("Field containing a time."))

config.action(
    config.registerAdapter, Time.getFactory, (ISchema,), name=Time.name)

config.action(
    config.registerAdapter, Time.getFactory, (schema.interfaces.ITime,))


# Timedelta
Timedelta = FieldFactory(
    'timedelta', schema.Timedelta, schema.interfaces.ITimedelta,
    title = _("Timedelta"),
    description = _("Field containing a timedelta."))

config.action(
    config.registerAdapter,Timedelta.getFactory,(ISchema,),name=Timedelta.name)

config.action(
    config.registerAdapter,Timedelta.getFactory,(schema.interfaces.ITimedelta,))


# EMail
EMail = FieldFactory(
    'email', EMail, IRFC822MailAddress,
    title = _('E-Mail'),
    description = _('A valid RFC822 email address field.'))

config.action(
    config.registerAdapter, EMail.getFactory, (ISchema,), name=EMail.name)

config.action(
    config.registerAdapter, EMail.getFactory, (IRFC822MailAddress,))


# URL
URL = FieldFactory(
    'url', URL, IBaseURL,
    title = _('URL'),
    description = _('A valid url field.'))

config.action(
    config.registerAdapter, URL.getFactory, (ISchema,), name = URL.name)

config.action(
    config.registerAdapter, URL.getFactory, (IBaseURL,))


# Choice
class ChoiceFieldFactory(FieldFactory):
    mapToField = ()
    mapToTextline = ('default', 'missing_value')


Choice = ChoiceFieldFactory(
    'choice', Choice, IChoice,
    _("Choice"), _('Field allow to select one value from list of values.'),
    ('vocabulary', 'vocabularyName'))

config.action(
    config.registerAdapter, Choice.getFactory, (ISchema,), name=Choice.name)

config.action(
    config.registerAdapter, Choice.getFactory, (schema.interfaces.IChoice,))


# List
List = FieldFactory(
    'list', List, schema.interfaces.IList,
    _("List"), _('Field allow to enter text lines.'),
    ('default', 'missing_value'))

config.action(
    config.registerAdapter, List.getFactory, (ISchema,), name=List.name)

config.action(
    config.registerAdapter, List.getFactory, (schema.interfaces.IList,))


# ChoiceList
ChoiceList = FieldFactory(
    'choicelist', ChoiceList, IChoiceList,
    _("Choice List"), _('Field allow to select values from list of values.'),
    ('default', 'missing_value', 'unique'))

config.action(
    config.registerAdapter, 
    ChoiceList.getFactory, (ISchema,), name=ChoiceList.name)

config.action(
    config.registerAdapter, 
    ChoiceList.getFactory, (IChoiceList,))


# RichText
RichText = FieldFactory(
    'richtext', RichText, IRichText,
    title = _("RichText"),
    description = _("RichText field."),
    hiddenFields = ('default', 'missing_value',))

config.action(
    config.registerAdapter, RichText.getFactory, (ISchema,), name=RichText.name)

config.action(
    config.registerAdapter, RichText.getFactory,(IRichText,))
