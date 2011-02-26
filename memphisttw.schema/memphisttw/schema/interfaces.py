from zope import interface, schema
from pyramid.i18n import TranslationStringFactory
from memphis import storage, contenttype

_ = TranslationStringFactory('memphis.schema')


class IVocabularyFactory(schema.interfaces.IVocabularyFactory):
    """ vocabulary factory """


class IFieldWithVocabulary(interface.Interface):
    """ field with configurable vocabulary """

    values = schema.Tuple(
        title = _(u'Values'),
        description = _(u'Enter values for field, each line new value.'),
        value_type = schema.TextLine(),
        required = True,
        unique = True,
        missing_value = [])


class IChoice(schema.interfaces.IChoice, IFieldWithVocabulary):
    """ choice """


class IChoiceList(schema.interfaces.IList, IFieldWithVocabulary):
    """ list of choices """


class ITuple(schema.interfaces.ITuple, IFieldWithVocabulary):
    """ tuple """


class IEMail(interface.Interface):
    """ email field """


class IURL(interface.Interface):
    """ url field """


class ICountry(schema.interfaces.ITextLine):
    """ Country field """


class IState(schema.interfaces.ITextLine):
    """ US State field """


# TTW Schema
class IField(interface.Interface):
    """ ttw field """

class ISchema(interface.Interface):
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


class ISchemaType(storage.ISchema):
    """ schema type """


class ISchemaManagement(contenttype.IContainer):
    """ schema management configlet """


class IFieldFactory(contenttype.IFactory):
    """ field factory """

    field = interface.Attribute('Field class')
