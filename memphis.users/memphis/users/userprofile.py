from memphis import controlpanel
from interfaces import _, IUserProfileConfiglet


controlpanel.registerConfiglet(
    name='principals.profile',
    schema=IUserProfileConfiglet,
    title = _('User profile'),
    description = _('This area allows you to configure user profile.'))
