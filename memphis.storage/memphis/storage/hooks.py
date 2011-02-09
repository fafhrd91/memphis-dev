import sqlalchemy, threading


local = threading.local()
metadata = sqlalchemy.MetaData()


def getSession():
    return getattr(local, 'session', None)


def setSession(session):
    local.session = session


def getMetadata():
    return metadata


def setMetadata(md):
    global metadata
    metadata = md
