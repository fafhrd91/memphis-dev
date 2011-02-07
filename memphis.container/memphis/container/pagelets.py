""" 

$Id: pagelets.py 4729 2011-02-03 05:26:47Z nikolay $
"""
from zope import interface
from memphis import view
from memphis.container.interfaces import IContained, IContainer


class IListing(interface.Interface):
    view.pageletType("container:listing", IContainer)
    

class IActions(interface.Interface):
    view.pageletType("container:actions", IContained)


class IAddingView(interface.Interface):
    view.pageletType("container:adding", IContainer)


class IAddingMenuView(interface.Interface):
    view.pageletType("container:addingmenu", IContainer)
