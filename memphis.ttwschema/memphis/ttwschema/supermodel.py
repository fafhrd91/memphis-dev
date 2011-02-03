""" config registrations for plone.supermodel

$Id: supermodel.py 4711 2011-02-02 22:55:35Z nikolay $
"""
from memphis import config
from plone.supermodel import converters, fields, serializer, parser


config.action(config.registerAdapter, converters.DefaultFromUnicode)
config.action(config.registerAdapter, converters.DefaultToUnicode)

config.action(config.registerAdapter, converters.DateFromUnicode)
config.action(config.registerAdapter, converters.DatetimeFromUnicode)

config.action(config.registerAdapter, converters.InterfaceFieldFromUnicode)
config.action(config.registerAdapter, converters.InterfaceFieldToUnicode)

config.action(config.registerAdapter, converters.ObjectFromUnicode)


config.action(config.registerUtility,
              fields.BytesHandler, name="zope.schema.Bytes")

config.action(config.registerUtility,
              fields.ASCIIHandler, name="zope.schema.ASCII")

config.action(config.registerUtility,
              fields.BytesLineHandler, name="zope.schema.BytesLine")

config.action(config.registerUtility,
              fields.ASCIILineHandler, name="zope.schema.ASCIILine")

config.action(config.registerUtility,
              fields.TextHandler, name="zope.schema.Text")

config.action(config.registerUtility,
              fields.TextLineHandler, name="zope.schema.TextLine")

config.action(config.registerUtility,
              fields.BoolHandler, name="zope.schema.Bool")

config.action(config.registerUtility,
              fields.IntHandler, name="zope.schema.Int")

config.action(config.registerUtility,
              fields.FloatHandler, name="zope.schema.Float")

config.action(config.registerUtility,
              fields.DecimalHandler, name="zope.schema.Decimal")

config.action(config.registerUtility,
              fields.TupleHandler, name="zope.schema.Tuple")

config.action(config.registerUtility,
              fields.ListHandler, name="zope.schema.List")

config.action(config.registerUtility,
              fields.SetHandler, name="zope.schema.Set")

config.action(config.registerUtility,
              fields.FrozenSetHandler, name="zope.schema.FrozenSet")

config.action(config.registerUtility,
              fields.PasswordHandler, name="zope.schema.Password")

config.action(config.registerUtility,
              fields.DictHandler, name="zope.schema.Dict")

config.action(config.registerUtility,
              fields.DatetimeHandler, name="zope.schema.Datetime")

config.action(config.registerUtility,
              fields.DateHandler, name="zope.schema.Date")

config.action(config.registerUtility,
              fields.SourceTextHandler, name="zope.schema.SourceText")

config.action(config.registerUtility,
              fields.URIHandler, name="zope.schema.URI")

config.action(config.registerUtility,
              fields.IdHandler, name="zope.schema.Id")

config.action(config.registerUtility,
              fields.DottedNameHandler, name="zope.schema.DottedName")

config.action(config.registerUtility,
              fields.InterfaceFieldHandler, name="zope.schema.InterfaceField")

config.action(config.registerUtility,
              fields.ObjectHandler, name="zope.schema.Object")

config.action(config.registerUtility,
              fields.ChoiceHandler, name="zope.schema.Choice")


config.action(config.registerAdapter, serializer.DefaultFieldNameExtractor)

config.action(config.registerUtility, parser.DefaultSchemaPolicy())
