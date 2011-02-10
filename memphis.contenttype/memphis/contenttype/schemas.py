from zope import interface, schema
from memphis import storage
from memphis.contenttype.interfaces import ISchemaType


class IDublinCore(interface.Interface):
    """ Dublin Core properties """
    storage.schema('content.dublincore', type=ISchemaType,
                   title = 'Dublin Core',
                   description = 'Dublin core properties.')

    title = schema.TextLine(
        title = u'Title',
        description =
        u"The first unqualified Dublin Core 'Title' element value.")

    description = schema.Text(
        title = u'Description',
        description =
        u"The first unqualified Dublin Core 'Description' element value.",
        required = False)

    created = schema.Datetime(
        title = u'Creation Date',
        description =
        u"The date and time that an object is created. "
        u"\nThis is normally set automatically.",
        required = False)

    modified = schema.Datetime(
        title = u'Modification Date',
        description =
        u"The date and time that the object was last modified in a\n"
        u"meaningful way.",
        required = False)

    effective = schema.Datetime(
        title = u'Effective Date',
        description =
        u"The date and time that an object should be published. ",
        required = False)

    expires = schema.Datetime(
        title = u'Expiration Date',
        description =
        u"The date and time that the object should become unpublished.",
        required = False)

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
        description =
        u"The first unqualified Dublin Core 'Publisher' element value.",
        required = False)

    contributors = schema.Tuple(
        title = u'Contributors',
        description =
        u"The unqualified Dublin Core 'Contributor' element values",
        value_type = schema.TextLine(),
        required = False)
