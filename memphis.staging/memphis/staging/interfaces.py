from zope import schema, interface
from memphis import storage


class IVersionItem(interface.Interface):
    """ version item behavior """


class IVersionsRelation(interface.Interface):
    """ relation for versions chaning """

    version = schema.Int(
        title = u'Version',
        default = 0,
        required = True)

    working = schema.Bool(
        title = u'Working copy',
        default = False,
        required = True)

    comment = schema.Text(
        title = u'Version comment',
        default = u'',
        required = False)

    date = schema.Datetime(
        title = u'Checkin datetime',
        required = False)


class IStagingBehavior(storage.ISchemaWrapper):
    """ staging behavior """

    def getWorkingCopy():
        """ get working cope """

    def checkin():
        """ checking working copy """

    def checkout(version):
        """ create working copy from version """

    def listVersions():
        """ list available versions """
