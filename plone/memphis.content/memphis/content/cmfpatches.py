""" various cmf/plone patches """
from memphis import config
from zope.site.interfaces import ILocalSiteManager
from zope.component import queryUtility, getUtilitiesFor, getSiteManager


#===========================================================
# add support TypeInformation as utility in TypesTools
#===========================================================
from Acquisition import aq_base
from Products.CMFCore.TypesTool import TypesTool
from Products.CMFCore.interfaces import ITypeInformation

orig_objectValues = TypesTool.objectValues

def objectValues(self, spec=None):
    lst = orig_objectValues(self, spec)
    ids = [ti.id for ti in lst]

    lst.extend([util for n, util in getUtilitiesFor(ITypeInformation)
                 if n not in ids])

    return lst


orig_getTypeInfo = TypesTool.getTypeInfo

def getTypeInfo(self, contentType):
    ti = orig_getTypeInfo(self, contentType)
    
    if ti is None:
        if not isinstance(contentType, basestring):
            if hasattr(aq_base(contentType), 'getPortalTypeName'):
                contentType = contentType.getPortalTypeName()
                if contentType is None:
                    return None
            else:
                return None
        ti = queryUtility(ITypeInformation, contentType)

    return ti
#===========================================================


@config.action
def patchTypesTool():
    TypesTool.objectValues = objectValues
    TypesTool.getTypeInfo = getTypeInfo
