""" fixme: remove schema from item in Behavior.remove method

$Id: behavior.py 11774 2011-01-30 07:39:51Z fafhrd91 $
"""
import sqlalchemy
from zope import interface
from memphis.storage.hooks import getSession
from memphis.storage.interfaces import IBehavior
from memphis.storage.exceptions import StorageException


class Behavior(object):
    interface.implements(IBehavior)

    def __init__(self, name, title, spec, relation, factory,
                 schema=None, description=''):
        self.name = name
        self.title = title
        self.description = description
        self.spec = spec
        self.schema = schema
        self.factory = factory
        self.relation = relation

    def apply(self, item):
        # run custom code
        if hasattr(self.factory, 'applyBehavior'):
            self.factory.applyBehavior(item, self)

        # apply behavior
        oid = item.oid
        session = getSession()

        ob = session.query(SQLBehavior).filter(
            sqlalchemy.and_(
                SQLBehavior.oid == oid, SQLBehavior.name == self.name)).first()
        if ob is not None:
            raise StorageException('Behavior already applied: %s'%self.name)

        num = len(self.getItemBehaviors(oid)) + 1
        session.add(SQLBehavior(oid, self.name, num))
        session.flush()

        # apply schema
        if self.schema is not None:
            item.applySchema(self.schema)

    def remove(self, item):
        oid = item.oid
        session = getSession()

        ob = session.query(SQLBehavior).filter(
            sqlalchemy.and_(
                SQLBehavior.oid == oid, SQLBehavior.name == self.name)).first()

        if ob is None:
            raise StorageException('Behavior is not applied: %s'%self.name)

        session.delete(ob)
        session.flush()

        if hasattr(self.factory, 'removeBehavior'):
            self.factory.removeBehavior(item, self)

    def __call__(self, item):
        from registry import getRelation

        if self.relation:
            return self.factory(
                item, getRelation(self.relation))
        else:
            return self.factory(item)

    def getBehaviorOIDs(self):
        for r in getSession().query(
            SQLBehavior.oid).filter(SQLBehavior.name == self.name):
            yield r[0]

    @classmethod
    def getItemBehaviors(self, oid):
        return [r[0] for r in getSession().query(
                SQLBehavior.name).filter(
                SQLBehavior.oid==oid).order_by(
                sqlalchemy.sql.expression.desc(SQLBehavior.inst_id))]


class SQLBehavior(object):

    def __init__(self, oid, name, inst_id=None):
        self.oid = oid
        self.name = name
        self.inst_id = inst_id
