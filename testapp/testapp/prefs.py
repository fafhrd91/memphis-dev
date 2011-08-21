"""

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
from zope import schema, interface
from memphis import config, preferences


class IMyPrefs(interface.Interface):

    title = schema.TextLine(
        title = u'My custom title')

    description = schema.Text(
        title = u'My custom description')


config.action(
    preferences.registerPreference,
    'membership.custom', IMyPrefs,
    title = 'My custom preferences',
    description = 'Description for custom preferences.')
