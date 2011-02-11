from rwproperty import getproperty, setproperty
from zope import interface, schema, component
from zope.schema import interfaces as schema_interfaces
from zope.interface.interface import InterfaceClass
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from z3c.schema.email import RFC822MailAddress
from z3c.schema.email.interfaces import IRFC822MailAddress
from z3c.schema.baseurl.field import isValidBaseURL, BaseURL
from z3c.schema.baseurl.interfaces import InvalidBaseURL, IBaseURL

from memphis import config
from memphis.ttwschema import interfaces, vocabulary
from memphis.ttwschema.interfaces import _, IFieldFactory


class Field(object):
    ignoreFields = ()


def FieldType(*args, **kw):
    pass


class FieldFactory(object):
    interface.implements(IFieldFactory)

    hiddenFields = ()
    mapToField = ('default', 'missing_value')

    def __init__(self, name, field, schema, title='', 
                 description='', hiddenFields = ()):
        self.name = name
        self.field = field
        self.title = title
        self.description = description
        self.field.__factory__ = self

        self.schema = self.wrapSchema(schema, field, hiddenFields)

    def __call__(self, **kw):
        return self.field(**kw)

    def wrapSchema(self, sch, field, hfields):
        wschema = InterfaceClass(sch.__name__, (interface.Interface,),
                                 __doc__ = sch.__doc__,
                                 __module__ = 'memphis.ttwschema.schemas')

        for name, fld in schema.getFieldsInOrder(sch):
            if name in ('readonly', 'order') or name in hfields:
                continue
            if fld.__class__ == schema.Field:
                if name not in self.mapToField:
                    continue
                fld = field(
                    __name__ = name,
                    title = fld.title,
                    description = fld.description,
                    required = False)

            wschema._InterfaceClass__attrs[name] = fld

        return wschema


class FactoryWrapper(object):
    component.adapts(interfaces.ISchema)
    interface.implements(interfaces.IFieldFactory)

    def __init__(self, factory):
        self.factory = factory

    def __call__(self, context):
        return self.factory


# Boolean
Bool = FieldFactory(
    'boolean', schema.Bool, schema_interfaces.IBool,
    title = _("Boolean"),
    description = _("Boolean field (YES or NO)."))

config.action(
    config.registerAdapter, 
    FactoryWrapper(Bool), (interfaces.ISchema,), name=Bool.name)


# Integer
Int = FieldFactory(
    'int', schema.Int, schema_interfaces.IInt,
    title = _("Integer"),
    description = _("Field containing an Integer Value."))

config.action(
    config.registerAdapter, 
    FactoryWrapper(Int), (interfaces.ISchema,), name = Int.name)


# Text
Text = FieldFactory(
    'text', schema.Text, schema_interfaces.IText,
    title = _("Text"),
    description = _("Field containing text with newlines."))

config.action(
    config.registerAdapter,
    FactoryWrapper(Text), (interfaces.ISchema,), name = Text.name)


# Text Line
TextLine = FieldFactory(
    'textline', schema.TextLine, schema_interfaces.ITextLine,
    title = _("Text Line"),
    description = _("Field containing text line without newlines."))

config.action(
    config.registerAdapter, 
    FactoryWrapper(TextLine), (interfaces.ISchema,), name = TextLine.name)


# Float
Float = FieldFactory(
    'float', schema.Float, schema_interfaces.IFloat,
    title = _("Float"),
    description = _("Field containing a Float."))

config.action(
    config.registerAdapter, 
    FactoryWrapper(Float), (interfaces.ISchema,), name = Float.name)


# Decimal
Decimal = FieldFactory(
    'decimal', schema.Decimal, schema_interfaces.IDecimal,
    title = _("Decimal"),
    description = _("Field containing a Dicmal."))

config.action(
    config.registerAdapter, 
    FactoryWrapper(Decimal), (interfaces.ISchema,), name = Decimal.name)


# Date
Date = FieldFactory(
    'date', schema.Date, schema_interfaces.IDate,
    title = _("Date"),
    description = _("Field containing a date."))

config.action(
    config.registerAdapter, 
    FactoryWrapper(Date), (interfaces.ISchema,), name = Date.name)

# Datetime
Datetime = FieldFactory(
    'datetime', schema.Datetime, schema_interfaces.IDatetime,
    title = _("DateTime"),
    description = _("Field containing a DateTime."))

config.action(
    config.registerAdapter, 
    FactoryWrapper(Datetime), (interfaces.ISchema,), name = Datetime.name)

# Time
Time = FieldFactory(
    'time', schema.Time, schema_interfaces.ITime,
    title = _("Time"),
    description = _("Field containing a time."))

config.action(
    config.registerAdapter, 
    FactoryWrapper(Time), (interfaces.ISchema,), name = Time.name)

# Timedelta
Time = FieldFactory(
    'timedelta', schema.Time, schema_interfaces.ITime,
    title = _("Timedelta"),
    description = _("Field containing a timedelta."))

config.action(
    config.registerAdapter, 
    FactoryWrapper(Time), (interfaces.ISchema,), name = Time.name)

# EMail
EMail = FieldFactory(
    'email', RFC822MailAddress, IRFC822MailAddress,
    title = _('E-Mail'),
    description = _('A valid RFC822 email address field.'))

config.action(
    config.registerAdapter, 
    FactoryWrapper(EMail), (interfaces.ISchema,), name = EMail.name)


# URL
class URL(BaseURL):
    interface.implements(IBaseURL)

    def _validate(self, value):
        if isValidBaseURL(value) and not value.endswith(':/'):
            return

        raise InvalidBaseURL(value)


URL = FieldFactory(
    'url', URL, IBaseURL,
    title = _('URL'),
    description = _('A valid url field.'))

config.action(
    config.registerAdapter, 
    FactoryWrapper(URL), (interfaces.ISchema,), name = URL.name)


# select
class Select(schema.Choice):
    interface.implements(interfaces.ISelect)

    def __init__(self, *args, **kw):
        self.explicitSelect = kw.pop('explicitSelect', False)
        if 'values' not in kw:
            kw['values'] = []
        super(Select, self).__init__(*args, **kw)

    @setproperty
    def values(self, values):
        self.vocabulary = SimpleVocabulary.fromValues(values)

    @getproperty
    def values(self):
        return [term.value for term in self.vocabulary]


#class RadioSelect(Field, RadioChoice):
#    interface.implements(interfaces.IRadioSelect)

#    __schema__ = DataProperty(interfaces.IRadioSelect)

#    def __init__(self, *args, **kw):
#        self.horizontal = kw.pop('horizontal', False)
#        super(RadioSelect, self).__init__(*args, **kw)

#    @setproperty
#    def values(self, values):
#        self.vocabulary = SimpleVocabulary.fromValues(values)

#    @getproperty
#    def values(self):
#        return [term.value for term in self.vocabulary]


class VocAccess(object):

    @setproperty
    def values(self, values):
        self.value_type.vocabulary = SimpleVocabulary.fromValues(values)

    @getproperty
    def values(self):
        return [term.value for term in self.value_type.vocabulary]


class MultiSelect(schema.List, VocAccess):
    interface.implements(interfaces.IMultiSelect)

    missing_value = []
    hiddenFields = Field.ignoreFields + ('unique', 'max_length', 'min_length')

    def __init__(self, values=(), *args, **kw):
        kw['default'] = []
        kw['value_type'] = schema.Choice(values=values)

        super(MultiSelect, self).__init__(*args, **kw)


class MultiCheckbox(schema.List, VocAccess):
    interface.implements(interfaces.IMultiCheckbox)

    missing_value = []
    hiddenFields = Field.ignoreFields + ('unique', 'max_length', 'min_length')

    def __init__(self, values=(), *args, **kw):
        kw['default'] = []
        kw['value_type'] = schema.Choice(values=values)

        super(MultiCheckbox, self).__init__(*args, **kw)


class Country(schema.Choice, schema.TextLine):
    interface.implements(interfaces.ICountry)

    hiddenFields = Field.ignoreFields + ('max_length', 'min_length')

    def __init__(self, *args, **kw):
        kw['vocabulary'] = vocabulary.countries

        super(Country, self).__init__(*args, **kw)


class State(schema.Choice, schema.TextLine):
    interface.implements(interfaces.IState)

    hiddenFields = Field.ignoreFields + ('max_length', 'min_length')

    def __init__(self, *args, **kw):
        kw['vocabulary'] = vocabulary.states

        super(State, self).__init__(*args, **kw)


class Lines(schema.Tuple):
    interface.implements(interfaces.ILines)

    missing_value = []

    def __init__(self, values=(), *args, **kw):
        kw['default'] = []
        kw['value_type'] = schema.TextLine()

        super(Lines, self).__init__(*args, **kw)
