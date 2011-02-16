from zope import schema, interface


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


class IStagingBehavior(interface.Interface):
    """ staging behavior """

    def checkin():
        """ checking working copy """

    def listVersions():
        """ list available versions """
