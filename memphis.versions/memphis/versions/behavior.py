import sqlalchemy
from zope import interface
from memphis import storage, config
from memphis.contenttype.interfaces import IBehaviorType
from memphis.versions.interfaces import \
    IVersionItem, IVersionsRelation, IVersionsSchema, IVersionsBehavior


config.action(
    storage.registerRelation,
    'content.versions', IVersionsRelation)


config.action(
    storage.registerSchema,
    'content.versions', IVersionsSchema,
    title = u'Versions')


class VersionItem(storage.BehaviorBase):
    storage.behavior('content.version-item', IVersionItem)


class VersionsBehavior(storage.BehaviorBase):
    interface.implements(IVersionsBehavior)
    storage.behavior('content.versions', relation=IVersionsRelation,
                     type = IBehaviorType,
                     schema = IVersionsSchema,
                     title = u'Versions',
                     description = u'Data versioning support for content.')

    def getLastVersion(self):
        context = self.__context__
        try:
            rel = self.__relation__.query(
                self.__relation__.Type.source == context.oid).order_by(
                sqlalchemy.sql.expression.desc(
                    self.__relation__.Type.version)).first()
        except StopIteration:
            rel = None

        if rel is None:
            item = storage.insertItem(IVersionItem)
            for sch in context.schemas:
                item.applySchema(sch)

            for schId in context.schemas:
                sch = storage.querySchema(schId)
                if sch is not None:
                    item.getDatasheet(schId).__load__(sch(context))

            self.__relation__.insert(self.oid, item.oid, version=1)
            content = item
            versionInfo = IVersionsSchema(content)
            versionInfo.proxy = context.oid
            versionInfo.version = 1
            versionInfo.comment = 'Create content.'
        else:
            content = rel.__destination__

        versionInfo = IVersionsSchema(content)
        if versionInfo.commit:
            item = storage.insertItem(IVersionItem)
            for sch in context.schemas:
                item.applySchema(sch)

            for schId in context.schemas:
                if schId == 'content.versions':
                    continue
                sch = storage.querySchema(schId)
                if sch is not None:
                    item.getDatasheet(schId).__load__(sch(content))

            self.__relation__.insert(self.oid, item.oid, version=rel.version+1)
            content = item
            versionInfo = IVersionsSchema(content)
            versionInfo.proxy = context.oid
            versionInfo.version = rel.version+1

        return content

    def wrapSchema(self, schema, item):
        return schema(self.getLastVersion())

    def listVersions(self):
        sch = storage.getSchema(IVersionsSchema)
        return sch.query(sch.Type.proxy == self.oid).order_by(
            sch.Type.version).all()
