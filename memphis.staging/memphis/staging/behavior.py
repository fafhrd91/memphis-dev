from zope import interface
from memphis import storage, config
from memphis.contenttype.interfaces import IBehaviorType
from memphis.staging.interfaces import \
    IVersionItem, IVersionsRelation, IStagingBehavior


config.action(
    storage.registerRelation,
    'content.staging', IVersionsRelation)


class VersionItem(storage.BehaviorBase):
    storage.behavior('content.staging-item', IVersionItem)


class StagingBehavior(storage.BehaviorBase):
    interface.implements(IStagingBehavior)
    storage.behavior('content.staging', relation=IVersionsRelation,
                     type = IBehaviorType,
                     title = u'Staging',
                     description = u'Basic staging behavior for content.')

    def getWorkingCopy(self):
        try:
            rel = self.__relation__.getReferences(
                self.oid, working=True).next()
        except StopIteration:
            rel = None

        if rel is None:
            try:
                version = self.__relation__.query(
                    self.__relation__.Type.oid == self.oid).order_by(
                    sqlalchemy.sql.expression.desc(
                        self.__relation__.Type.version)).next().version + 1
            except:
                version = 1

            context = self.__context__
            item = storage.insertItem(IVersionItem)
            for sch in context.schemas:
                item.applySchema(sch)

            for schId in context.schemas:
                sch = storage.querySchema(schId)
                if sch is not None:
                    item.getDatasheet(schId).__load__(
                        sch.getDatasheet(context.oid))

            self.__relation__.insert(self.oid, item.oid, 
                                     working=True, version=version)
            return item
        else:
            return rel.__destination__

    def wrapSchema(self, schema, item):
        return schema(self.getWorkingCopy())

    def listVersions(self):
        versions = list(self.__relation__.getReferences(self.oid))
        versions.sort(key = lambda r: r.version)
        return versions
