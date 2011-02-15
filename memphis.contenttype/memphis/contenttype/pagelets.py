""" content specific pagelets """
from zope import interface
from memphis import view
from memphis.contenttype.interfaces import IContent, IContainer


class IContentActions(interface.Interface):
    view.pageletType('content-actions', IContent)


class IListing(interface.Interface):
    view.pageletType("container-listing", IContainer)


class IAddingView(interface.Interface):
    view.pageletType("container-adding", IContainer)


class IAddingMenuView(interface.Interface):
    view.pageletType("container-addingmenu", IContainer)
