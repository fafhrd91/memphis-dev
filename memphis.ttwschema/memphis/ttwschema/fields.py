"""

$Id: fields.py 11490 2009-12-07 09:29:34Z bubenkoff $
"""
from rwproperty import getproperty, setproperty
from zope import interface, schema
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from z3c.schema.email import RFC822MailAddress
from z3c.schema.baseurl.field import isValidBaseURL, BaseURL
from z3c.schema.baseurl.interfaces import InvalidBaseURL

#from z3ext.richtext.field import RichText
#from z3ext.widget.list.field import SimpleList
#from z3ext.widget.radio.field import RadioChoice

from memphis import config
from memphis.ttwschema import interfaces, vocabulary

_ = interfaces._


class Field(object):
    ignoreFields = ()


def FieldType(*args, **kw):
    pass


class FieldFactory(object):
    interface.implements(interfaces.IFieldFactory)

    ignoreFields = (
        'missing_value', 'default', 'readonly', 'value_type', 'order')

    def __init__(self, name, field, schema, title='', description='',
                 ignoreFields = ()):
        self.name = name
        self.field = field
        self.schema = schema
        self.title = title
        self.description = description
        self.ignoreFields = self.ignoreFields + ignoreFields

        self.field.__factory__ = self

    def __call__(self, **kw):
        return self.field(**kw)


Bool = FieldFactory(
    'boolean', schema.Bool, interfaces.IBool,
    title = _("Boolean"),
    description = _("Boolean field (YES or NO)."),
    ignoreFields = ('min_length', 'max_length'))

config.action(
    config.registerUtility, Bool, name = Bool.name)


Int = FieldFactory(
    'int', schema.Int, interfaces.IInt,
    title = _("Integer"),
    description = _("Field containing an Integer Value."))

config.action(
    config.registerUtility, Int, name = Int.name)


Text = FieldFactory(
    'Text', schema.Text, interfaces.IText,
    title = _("Text"),
    description = _("Field containing text with newlines."),
    ignoreFields = ('min_length', 'max_length'))

config.action(
    config.registerUtility, Text, name = Text.name)


TextLine = FieldFactory(
    'TextLine', schema.TextLine, interfaces.ITextLine,
    title = _("Text Line"),
    description = _("Field containing text line without newlines."),
    ignoreFields = ('min_length', 'max_length'))

config.action(
    config.registerUtility, TextLine, name = TextLine.name)


Date = FieldType(
    'Date', schema.Date, interfaces.IDate)

Datetime = FieldType(
    'Datetime', schema.Datetime, interfaces.IDatetime)

Time = FieldType(
    'Time', schema.Time, interfaces.ITime)

EMail = FieldType(
    'EMail', RFC822MailAddress, interfaces.IEmailField,
    ignoreFields = Field.ignoreFields + ('max_length', 'min_length'))

#RichText = FieldType(
#    'RichText', RichText, interfaces.IRichText)


class URL(Field, BaseURL):
    interface.implements(interfaces.IURLField)

    def _validate(self, value):
        if isValidBaseURL(value) and not value.endswith(':/'):
            return

        raise InvalidBaseURL(value)


class Select(Field, schema.Choice):
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


class MultiSelect(Field, schema.List, VocAccess):
    interface.implements(interfaces.IMultiSelect)

    missing_value = []
    ignoreFields = Field.ignoreFields + ('unique', 'max_length', 'min_length')

    def __init__(self, values=(), *args, **kw):
        kw['default'] = []
        kw['value_type'] = schema.Choice(values=values)

        super(MultiSelect, self).__init__(*args, **kw)


class MultiCheckbox(Field, schema.List, VocAccess):
    interface.implements(interfaces.IMultiCheckbox)

    missing_value = []
    ignoreFields = Field.ignoreFields + ('unique', 'max_length', 'min_length')

    def __init__(self, values=(), *args, **kw):
        kw['default'] = []
        kw['value_type'] = schema.Choice(values=values)

        super(MultiCheckbox, self).__init__(*args, **kw)


class Country(Field, schema.Choice, schema.TextLine):
    interface.implements(interfaces.ICountry)

    ignoreFields = Field.ignoreFields + ('max_length', 'min_length')

    def __init__(self, *args, **kw):
        kw['vocabulary'] = vocabulary.countries

        super(Country, self).__init__(*args, **kw)


class State(Field, schema.Choice, schema.TextLine):
    interface.implements(interfaces.IState)

    ignoreFields = Field.ignoreFields + ('max_length', 'min_length')

    def __init__(self, *args, **kw):
        kw['vocabulary'] = vocabulary.states

        super(State, self).__init__(*args, **kw)


class Lines(Field, schema.Tuple):
    interface.implements(interfaces.ILines)

    missing_value = []

    def __init__(self, values=(), *args, **kw):
        kw['default'] = []
        kw['value_type'] = schema.TextLine()

        super(Lines, self).__init__(*args, **kw)
