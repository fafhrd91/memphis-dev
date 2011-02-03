"""

$Id: hooks.py 11737 2011-01-27 23:14:43Z fafhrd91 $
"""
import sqlalchemy, threading


local = threading.local()
local.metadata = sqlalchemy.MetaData()


def getSession():
    return getattr(local, 'session', None)


def setSession(session):
    local.session = session


def getMetadata():
    return getattr(local, 'metadata', None)


def setMetadata(md):
    local.metadata = md
