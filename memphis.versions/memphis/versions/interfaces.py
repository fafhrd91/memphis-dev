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


class IVersionsSchema(interface.Interface):
    """ versions schema """

    proxy = schema.TextLine(
        title = u'Proxy oid',
        required = False)

    date = schema.Datetime(
        title = u'Checkin datetime',
        required = False)

    version = schema.Int(
        title = u'Version',
        required = True)

    comment = schema.TextLine(
        title = u'Modification note',
        default = u'',
        required = False)

    commit = schema.Bool(
        title = u'Create new version',
        default = False,
        required = False)


class IVersionsBehavior(storage.ISchemaWrapper):
    """ versions behavior """

    def getWorkingCopy():
        """ get working cope """

    def checkin():
        """ checking working copy """

    def checkout(version):
        """ create working copy from version """

    def listVersions():
        """ list available versions """
