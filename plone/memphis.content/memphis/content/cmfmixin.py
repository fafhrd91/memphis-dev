""" cmf content mixin """
from zope import interface
from zope.annotation import IAttributeAnnotatable
from zope.dublincore.interfaces import IDCDescriptiveProperties
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from memphis import config

from Acquisition import aq_parent
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.interfaces import IContentish, IDynamicType
from Products.CMFCore.Expression import getExprContext
from Products.CMFCore.CMFCatalogAware import CatalogAware, WorkflowAware


class CMFMixin(CatalogAware, WorkflowAware, SimpleItem):
    interface.implements(IAttributeAnnotatable, IContentish, IDynamicType)

    __type__ = None

    @property
    def __parent__(self):
        return aq_parent(self)

    @property
    def meta_type(self):
        return self.__type__.id

    @property
    def portal_type(self):
        return self.__type__.id

    def _setId(self, id):
        self.id = id
        self.__name__ = id

    def getTypeInfo(self):
        return self.__type__

    def getPortalTypeName(self):
        return self.__type__.id

    def getActionInfo(self,action_chain,check_visibility=0,check_condition=0):
        return self.__type__.getActionInfo(
            action_chain, self, check_visibility, check_condition)

    def getIconURL(self):
        icon_expr_object = self.__type__.getIconExprObject()
        if icon_expr_object is None:
            return ''
        ec = getExprContext(self)
        return icon_expr_object(ec)

    def Type(self):
        return self.__type__.id
        
    def Title(self):
        return IDCDescriptiveProperties(self).title

    def Description(self):
        return IDCDescriptiveProperties(self).description


@config.handler(CMFMixin, IObjectModifiedEvent)
def reindexCMFMixin(ob, ev):
    ob.reindexObject()
