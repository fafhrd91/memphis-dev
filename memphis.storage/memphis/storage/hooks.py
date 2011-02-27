import sqlalchemy, threading


local = threading.local()
metadata = sqlalchemy.MetaData()


def getSession():
    return getattr(local, 'session', None)


def endSession():
    cache.endSession(getattr(local, 'session', None))
    local.session = None


def setSession(session):
    local.session = session


def getMetadata():
    return metadata


def setMetadata(md):
    global metadata
    metadata = md


UNSET = object()

class Cache(object):

    items = {}
    datasheets = {}

    def endSession(self, session):
        Cache.items.clear()
        Cache.datasheets.clear()

    def getItem(self, oid, default=UNSET):
        return Cache.items.get(oid, default)

    def setItem(self, oid, item):
        Cache.items[oid] = item

    def delItem(self, oid):
        if oid in Cache.items:
            del Cache.items[oid]

    def getDatasheet(self, oid, klass):
        return Cache.datasheets.get((oid, klass))

    def setDatasheet(self, oid, klass, ds):
        Cache.datasheets[(oid, klass)] = ds

    def delDatasheet(self, oid, klass):
        key = (oid, klass)
        if key in Cache.datasheets:
            del Cache.datasheets[key]


cache = Cache()
