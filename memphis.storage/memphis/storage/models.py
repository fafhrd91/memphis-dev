import sqlalchemy, sqlalchemy.orm
from memphis.storage.item import Item
from memphis.storage.schema import SQLSchema
from memphis.storage.behavior import SQLBehavior
from memphis.storage.relation import Reference


def initializeModels(MetaData):
    # items table
    sqlItems = sqlalchemy.Table(
        'items', MetaData,
        sqlalchemy.Column('oid', sqlalchemy.String(32), primary_key = True),
        sqlalchemy.Column('type', sqlalchemy.String(255)))

    sqlalchemy.orm.mapper(Item, sqlItems)

    # behavior table
    sqlBehavior = sqlalchemy.Table(
        'behavior', MetaData,
        sqlalchemy.Column(
            'oid', sqlalchemy.Unicode(32),
            sqlalchemy.ForeignKey(
                'items.oid', onupdate="CASCADE", ondelete="CASCADE"),
            primary_key = True),
        sqlalchemy.Column(
            'name', sqlalchemy.Unicode(255), primary_key = True),
        sqlalchemy.Column('inst_id', sqlalchemy.Integer),
        )

    sqlalchemy.orm.mapper(SQLBehavior, sqlBehavior)

    # relations table
    sqlReference = sqlalchemy.Table(
        'reference', MetaData,
        sqlalchemy.Column(
            'oid', sqlalchemy.Unicode(32)),
        sqlalchemy.Column(
            'source', sqlalchemy.Unicode(32),
            sqlalchemy.ForeignKey(
                'items.oid', onupdate="CASCADE", ondelete="CASCADE")
            , primary_key=True),
        sqlalchemy.Column(
            'destination', sqlalchemy.Unicode(32),
            sqlalchemy.ForeignKey(
                'items.oid', onupdate="CASCADE", ondelete="CASCADE")
            , primary_key=True),
        sqlalchemy.Column('type', sqlalchemy.Unicode(255), primary_key=True),
        )

    sqlalchemy.orm.mapper(Reference, sqlReference)

    # schema table
    sqlSchema = sqlalchemy.Table(
        'schema', MetaData,
        sqlalchemy.Column(
            'oid', sqlalchemy.Unicode(32),
            sqlalchemy.ForeignKey(
                'items.oid', onupdate="CASCADE", ondelete="CASCADE"),
            primary_key = True),
        sqlalchemy.Column(
            'name', sqlalchemy.Unicode(255), primary_key = True),
        )

    sqlalchemy.orm.mapper(SQLSchema, sqlSchema)
