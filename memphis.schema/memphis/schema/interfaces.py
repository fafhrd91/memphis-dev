from zope import interface, schema
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('memphis.schema')


# TTW Schema
class IField(interface.Interface):
    """ ttw field """


class IFieldInformation(interface.Interface):
    """ field information """

    field = interface.Attribute('Field class')
    title = interface.Attribute('Title')
    description = interface.Attribute('Description')


# Widgets management configlet
class IWidgetsManagement(interface.Interface):
    """ widget management configlet """

    data = schema.Dict(
        title = u'Mapping data',
        required = True)
