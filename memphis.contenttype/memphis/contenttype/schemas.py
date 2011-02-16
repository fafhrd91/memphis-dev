""" additional schemas """
import pytz, datetime
from zope import interface, schema
from memphis import storage
from memphis.contenttype.interfaces import ISchemaType


class IDCPublishing(interface.Interface):
    """Publishing properties"""
    storage.schema('content.dc.publishing', type=ISchemaType,
                   title = 'Dublin Core Pubishing',
                   description = 'Dublin core publishing properties.')

    effective = schema.Datetime(
        title = u'Effective Date',
        description = u"The date and time that an object should be published.",
        required = False)

    expires = schema.Datetime(
        title = u'Expiration Date',
        description = \
            u"The date and time that the object should become unpublished.",
        required = False)


class IDCExtended(interface.Interface):
    """Extended properties

    This is a mixed bag of properties we want but that we probably haven't
    quite figured out yet.
    """
    storage.schema('content.dc.extended', type=ISchemaType,
                   title = 'Dublin Core Extended',
                   description = 'Dublin Core extended properties.')

    creators = schema.Tuple(
        title = u'Creators',
        description = u"The unqualified Dublin Core 'Creator' element values",
        value_type = schema.TextLine(),
        required = False)

    subjects = schema.Tuple(
        title = u'Subjects',
        description = u"The unqualified Dublin Core 'Subject' element values",
        value_type = schema.TextLine(),
        required = False)

    publisher = schema.Text(
        title = u'Publisher',
        description =\
            u"The first unqualified Dublin Core 'Publisher' element value.",
        required = False)

    contributors = schema.Tuple(
        title = u'Contributors',
        description = \
            u"The unqualified Dublin Core 'Contributor' element values",
        value_type = schema.TextLine(),
        required = False)
