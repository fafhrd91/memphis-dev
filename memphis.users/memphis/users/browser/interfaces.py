"""

$Id: interfaces.py 11798 2011-01-31 04:14:24Z fafhrd91 $
"""
from zope import interface


class IPersonalPasswordForm(interface.Interface):
    """ marker interface for personal form """


class IPrincipalPasswordForm(interface.Interface):
    """ marker interface """
