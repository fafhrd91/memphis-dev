""" 

$Id: pagelets.py 4729 2011-02-03 05:26:47Z nikolay $
"""
from zope import interface
from memphis import view
from memphis.container.interfaces import IManageableContainer


class IListingView(interface.Interface):
    view.pageletType("container:listing", IManageableContainer)


class IAddingView(interface.Interface):
    view.pageletType("container:adding", IManageableContainer)


class IAddingMenuView(interface.Interface):
    view.pageletType("container:addingmenu", IManageableContainer)
