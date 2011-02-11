"""

$Id: interfaces.py 11173 2009-11-06 00:41:05Z bubenkoff $
"""
from zope import interface, schema
from z3c.schema.email import RFC822MailAddress
from z3c.schema.email.interfaces import IRFC822MailAddress
from pyramid.i18n import TranslationStringFactory
from memphis import storage, container

_ = TranslationStringFactory('memphis.ttwschema')


class IField(interface.Interface):
    """ ttw field """


class IFieldFactory(container.IFactory):
    """ field factory """


class IFieldWithValues(interface.Interface):
    """ field with configurable values """

    values = schema.List(
        title = _(u'Values'),
        description = _(u'Enter values for field, each line new value.'),
        value_type = schema.TextLine(),
        required = True,
        unique = True,
        missing_value = [])


class ISelect(schema.interfaces.IChoice, IFieldWithValues):
    """ select field """

    explicitSelect = schema.Bool(
        title=_(u'Use explicit value selection for required fields'),
        default=False)


#class IRadioSelect(IRadioChoice, IFieldWithVocabulary):
#    """ select using radio buttons """
#
#    horizontal = schema.Bool(
#        title=_(u'Use horizontal layout'),
#        default=False)


class IMultiSelect(schema.interfaces.IList, IFieldWithValues):
    """ multi select """


class IMultiCheckbox(schema.interfaces.IList, IFieldWithValues):
    """ multi checkbox select """


class ICountry(schema.interfaces.ITextLine):
    """ Country field """


class IState(schema.interfaces.ITextLine):
    """ US State field """


class ILines(schema.interfaces.ITuple):
    """ Lines field """


class ISchema(container.IContained):
    """ behavior/model for ttw schema """
    storage.schema('memphis.ttwschema')

    title = schema.TextLine(
        title = u'Title',
        required = True)

    description = schema.Text(
        title = u'Description',
        required = False)

    model = schema.Text(
        title = u'Model',
        default = u'')


class ISchemaManagement(container.IContainer):
    """ schema management configlet """


class ISchemaType(storage.ISchema):
    """ schema type """
