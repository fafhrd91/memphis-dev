import uuid
import sqlalchemy
import sqlalchemy.orm
from zope import interface
from memphis.storage import hooks
from memphis.storage.hooks import getSession
from memphis.storage.table import buildTable
from memphis.storage.datasheet import DatasheetType
from memphis.storage.interfaces import IRelation, IReference


class Reference(object):
    interface.implements(IReference)

    def __init__(self, oid, type, source, destination, **kw):
        self.oid = oid
        self.type = type
        self.source = source
        self.destination = destination

        for attr, value in kw.items():
            setattr(self, attr, value)

    @property
    def __source__(self):
        return hooks.getItem(self.source)

    @property
    def __destination__(self):
        return hooks.getItem(self.destination)


class Relation(object):
    interface.implements(IRelation)

    def __init__(self, name, Type, title=u'', description=u''):
        self.name = name
        self.Type = Type
        self.title = title
        self.description = description

    def __getitem__(self, oid):
        rel = getSession().query(self.Type).filter(
            self.Type.oid == oid).first()
        if rel is None:
            raise KeyError(oid)

        rel.type = self.name
        return rel

    def get(self, oid, default=None):
        try:
            return self[oid]
        except KeyError:
            return default

    def insert(self, source, destination, **kw):
        oid = uuid.uuid1().hex

        session = getSession()
        session.add(Reference(oid, self.name, source, destination))

        item = self.Type(oid, self.name, source, destination, **kw)
        session.add(item)
        session.flush()
        return self.get(oid)

    def remove(self, oid):
        session = getSession()

        ob = session.query(Reference).filter(Reference.oid == oid).first()
        if ob is None:
            raise KeyError(oid)
        session.delete(ob)

        ob = session.query(self.Type).filter(self.Type.oid == oid).first()
        if ob is not None:
            session.delete(ob)

        session.flush()

    def getReferences(self, source=None, destination=None, **kw):
        session = getSession()

        filter = []
        if source is not None:
            filter.append(self.Type.source == source)

        if destination is not None:
            filter.append(self.Type.destination == destination)

        for name, value in kw.items():
            if hasattr(self.Type, name):
                filter.append(getattr(self.Type, name)==value)

        if filter:
            for rel in session.query(self.Type).filter(
                sqlalchemy.and_(*filter)):
                yield rel
        else:
            for rel in session.query(self.Type):
                yield rel

    def query(self, *args):
        session = getSession()
        return session.query(self.Type).filter(*args)

    @classmethod
    def getItemReferences(cls, oid, type=None):
        if type is None:
            return getSession().query(Reference).filter(Reference.source == oid)
        else:
            return getSession().query(Reference).filter(
                sqlalchemy.and_(
                    Reference.source == oid,
                    Reference.type == type))

    @classmethod
    def getItemBackReferences(cls, oid, type=None):
        if type is None:
            return getSession().query(Reference).filter(
                    Reference.destination == oid).all()
        else:
            return getSession().query(Reference).filter(
                sqlalchemy.and_(
                    Reference.destination == oid,
                    Reference.type == type)).all()


def buildRelation(name, schema, title, description,
                  reserved = ('oid', 'source', 'destination')):
    columns = [
        sqlalchemy.Column('oid', sqlalchemy.Unicode(32),
                          sqlalchemy.ForeignKey('reference.oid'),
                          primary_key=True),
        sqlalchemy.Column('source', sqlalchemy.Unicode(32),
                          sqlalchemy.ForeignKey('items.oid')),
        sqlalchemy.Column('destination', sqlalchemy.Unicode(32),
                          sqlalchemy.ForeignKey('items.oid')),
        ]

    table = buildTable(name, 'relation', schema, columns, reserved)

    klass = DatasheetType(name, schema, Reference, None, title, description)
    klass.relationMapper = sqlalchemy.orm.mapper(klass, table)

    return Relation(name, klass, title, description)
