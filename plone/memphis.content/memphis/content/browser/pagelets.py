""" content pagelets """
from zope import interface
from memphis import view, content


class IDatasheetForm(interface.Interface):
    view.pageletType('content-datasheet', content.IDatasheet)
