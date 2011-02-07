from zope import interface
from memphis import config, storage
from interfaces import IContent


config.action(
    storage.registerSchema,
    'content.item', IContent)


class Content(storage.BehaviorBase):
    interface.implements(IContent)
    storage.behavior('content.item',
                     schema = IContent,
                     title = 'Content item',
                     description = 'Base behavior for content items.')
