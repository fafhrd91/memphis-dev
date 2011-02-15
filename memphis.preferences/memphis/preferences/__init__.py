# memphis.preferences public API

from memphis import config
from memphis.preferences.api import registerCategory
from memphis.preferences.api import registerPreference
from memphis.preferences.interfaces import _, IPreferences


config.action(
    registerCategory,
    'portal', _('Portal preferences'),
     _('These are all the preferences related to common portal settings.'))

config.action(
    registerCategory,
    'membership', _('Membership preferences'),
    _('These are all the preferences related to portal membership.'))
