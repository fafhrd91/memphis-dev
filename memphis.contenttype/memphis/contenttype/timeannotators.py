"""Objects that take care of annotating dublin core meta data times"""
import pytz
from datetime import datetime
from zope.lifecycleevent import IObjectModifiedEvent, IObjectCreatedEvent

from memphis import config
from memphis.contenttype.interfaces import IContent, IDCTimes


@config.handler(IContent, IObjectModifiedEvent)
def ModifiedAnnotator(object, event=None):
    dc = IDCTimes(object, None)
    if dc is not None:
        dc.modified = datetime.now(pytz.utc)


@config.handler(IContent, IObjectModifiedEvent)
def CreatedAnnotator(object, event=None):
    dc = IDCTimes(object, None)
    if dc is not None:
        now = datetime.now(pytz.utc)
        dc.created = now
        dc.modified = now
