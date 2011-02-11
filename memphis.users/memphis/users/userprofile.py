from memphis import config, controlpanel

from interfaces import _, IUserProfileConfiglet

config.action(
    controlpanel.registerConfiglet,
    name='principals.profile',
    schema=IUserProfileConfiglet,
    title = _('User profile'),
    description = _('This area allows you to configure user profile.'))
