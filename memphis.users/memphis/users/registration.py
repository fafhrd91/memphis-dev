from zope import interface
from memphis import controlpanel

from interfaces import _, ISiteRegistration


class SiteRegistration(object):
    interface.implements(ISiteRegistration)



controlpanel.registerConfiglet(
    'principals.registration', ISiteRegistration, SiteRegistration,
    _("Site registration"), _("Site registration configuration."))
