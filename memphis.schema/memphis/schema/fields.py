from rwproperty import setproperty
from zope import interface, schema, component
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from z3c.schema.email import RFC822MailAddress
from z3c.schema.baseurl.field import isValidBaseURL, BaseURL
from z3c.schema.baseurl.interfaces import InvalidBaseURL

from memphis import config
from memphis.form.browser.checkbox import CheckBoxWidget
from memphis.form.browser.select import MultiSelectWidget

from memphis.schema import interfaces


# Choice
class Choice(schema.Choice):
    interface.implements(interfaces.IChoice)

    def __init__(self, *args, **kw):
        if 'values' not in kw:
            kw['values'] = []
        super(Choice, self).__init__(*args, **kw)

    @property
    def values(self):
        return [term.value for term in self.vocabulary]

    @setproperty
    def values(self, values):
        self.vocabulary = SimpleVocabulary.fromValues(values)


# EMail
class EMail(RFC822MailAddress):
    interface.implements(interfaces.IEMail)


# URL
class URL(BaseURL):
    interface.implements(interfaces.IURL)

    def _validate(self, value):
        if isValidBaseURL(value) and not value.endswith(':/'):
            return

        raise InvalidBaseURL(value)


# List
class List(schema.List):

    missing_value = []


# SequenceList
class ChoiceList(schema.List):
    interface.implements(interfaces.IChoiceList)

    def __init__(self, values=(), *args, **kw):
        kw['default'] = []
        kw['missing_value'] = []
        kw['value_type'] = schema.Choice(values=values)

        super(ChoiceList, self).__init__(*args, **kw)

    @property
    def values(self):
        return [term.value for term in self.value_type.vocabulary]

    @setproperty
    def values(self, values):
        self.value_type.vocabulary = SimpleVocabulary.fromValues(values)


config.action(
    config.registerAdapter, 
    CheckBoxWidget, (interfaces.IChoiceList, None))

config.action(
    config.registerAdapter, 
    CheckBoxWidget, (interfaces.IChoiceList, None), name='checkbox')

config.action(
    config.registerAdapter, 
    MultiSelectWidget, (interfaces.IChoiceList, None), name='multiselect')
