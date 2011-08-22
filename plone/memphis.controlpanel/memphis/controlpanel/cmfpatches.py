""" various cmf/plone patches 

First of all, lets check if memphis configlet available as plone's configlet::

    >>> from Products.CMFPlone.PloneControlPanel import PloneControlPanel

    >>> cp = PloneControlPanel()
    >>> cp.listActions()
    ()

    >>> from zope import interface, schema, component
    >>> from memphis import controlpanel

    >>> class IMyConfiglet(interface.Interface):
    ...     
    ...     title = schema.TextLine(
    ...         title = u'Title',
    ...         default = u'test title',
    ...         required = True)

    >>> controlpanel.registerConfiglet(
    ...     'myconfiglet', IMyConfiglet)

    >>> cl = component.getUtility(IMyConfiglet)
    >>> IMyConfiglet.providedBy(cl)
    True

    >>> from Products.CMFPlone.PloneControlPanel import PloneControlPanel

    >>> actions = cp.listActions()
    >>> actions
    (<PloneConfiglet at myconfiglet>,)

    >>> actions[0].id,actions[0].title,actions[0].category, actions[0].permissions
    ('myconfiglet', 'myconfiglet', 'Products', ('Manage portal',))

Let's register another configlet::

    >>> class IMyConfiglet2(interface.Interface):
    ...     
    ...     title = schema.TextLine(
    ...         title = u'Title',
    ...         default = u'test title',
    ...         required = True)

    >>> controlpanel.registerConfiglet(
    ...     'myconfiglet2', IMyConfiglet2,
    ...     title = 'My configlet2',
    ...     category = 'Plone',
    ...     permission = 'zope.View')

    >>> actions = cp.listActions()
    >>> actions[1].id,actions[1].title,actions[1].category, actions[1].permissions
    ('myconfiglet2', 'My configlet2', 'Plone', ('zope.View',))

Let's test addons::

    >>> from Products.CMFPlone.QuickInstallerTool import QuickInstallerTool

    >>> class FakePortalSetup(object):
    ...     def listProfileInfo(self, *args):
    ...         return ()

    >>> qi = QuickInstallerTool()
    >>> qi.portal_setup = FakePortalSetup()

    >>> qi.listInstallableProducts()
    [{'status': 'new', 'hasError': False, 'id': 'Marshall', 'title': 'Marshall'}]

Let's define addon::

    >>> from memphis import config

    >>> addonRegistry = config.registry(
    ...     'test',
    ...     title = 'My test addon',
    ...     description = 'My test addon description',
    ...     addon = True)

    >>> qi.listInstallableProducts()[-1]
    {'status': 'new', 'hasError': False, 'id': 'test', 'description': 'My test addon description', 'title': 'My test addon'}

Install addon:

    >>> from zope.component.hooks import setSite
    >>> from zope.component import globalSiteManager
    >>> from zope.component.globalregistry import BaseGlobalComponents

    >>> reg = BaseGlobalComponents()
    >>> reg.__bases__ = (globalSiteManager,)

    >>> class Site(object):
    ...     def __init__(self, sm):
    ...         self.sm = sm
    ...     def getSiteManager(self):
    ...         return self.sm

    >>> setSite(Site(reg))

    >>> reg.__bases__
    (<BaseGlobalComponents base>,)

    >>> qi.installProduct('test')

    >>> reg.__bases__
    (<Registry test>, <BaseGlobalComponents base>)

    >>> qi.listInstalledProducts()
    [{'status': 'new', 'hasError': False, 'description': 'My test addon description', 'title': 'My test addon', 'isLocked': False, 'isHidden': False, 'id': 'test'}]

    >>> qi.upgradeInfo('test')
    {'required': False}

    >>> qi.isProductAvailable('test')
    True

    >>> qi.uninstallProducts(('test',))

    >>> reg.__bases__
    (<BaseGlobalComponents base>,)

    >>> qi.uninstallProducts(('Marshall',))
    Traceback (most recent call last):
    ...
    AttributeError: Marshall

"""

import logging
from zope.site.interfaces import ILocalSiteManager
from zope.component import queryUtility, getUtilitiesFor, getSiteManager

from memphis import config
from memphis.controlpanel.interfaces import IPloneConfiglet


#===========================================================
# add support PloneConfiglet as utility in PloneControlPanel
#===========================================================
from Products.CMFPlone.PloneControlPanel import PloneControlPanel

origin_listActions = PloneControlPanel.listActions

def PloneControlPanel_listActions(self, info=None, object=None):
    actions = origin_listActions(self, info, object)
    
    configlets = tuple(
        pc.__of__(self) for _, pc in getUtilitiesFor(IPloneConfiglet))
    
    return actions + configlets


#==============================
# add support Addons as utility
#==============================
from Products.CMFPlone.QuickInstallerTool import \
    QuickInstallerTool as PQuickInstallerTool
from Products.CMFQuickInstallerTool.InstalledProduct import InstalledProduct
from Products.CMFQuickInstallerTool.QuickInstallerTool import QuickInstallerTool

orig_listInstallableProducts = QuickInstallerTool.listInstallableProducts

def QI_listInstallableProducts(self, skipInstalled=True):
    addons = orig_listInstallableProducts(self, skipInstalled)

    curr_sm = getSiteManager()

    has = False
    for sm in config.getRegistry():
        if sm.addon and sm not in curr_sm.__bases__:
            has = True
            addons.append(
                {'title': sm.title, 'description': sm.description,
                 'status': 'new', 'hasError': False, 'id': sm.__name__})
    if has:
        addons.sort(key = lambda i: i['title'])
    return addons


orig_listInstalledProducts = QuickInstallerTool.listInstalledProducts

def QI_listInstalledProducts(self, showHidden=False):
    addons = orig_listInstalledProducts(self, showHidden)

    curr_sm = getSiteManager()

    has = False
    for sm in config.getRegistry():
        if sm.addon and sm in curr_sm.__bases__:
            has = True
            addons.append(
                {'title': sm.title, 'description': sm.description,
                 'status': 'new', 'hasError': False, 
                 'isLocked': False, 'isHidden': False,
                 'id': sm.__name__})
    if has:
        addons.sort(key = lambda i: i['title'])
    return addons


orig_installProduct = QuickInstallerTool.installProduct

def QI_installProduct(self, p, locked=False, hidden=False,
                      swallowExceptions=None, reinstall=False,
                      forceProfile=False, omitSnapshots=True, profile=None):

    reg = config.getRegistry(p)
    if reg is not None:
        sm = getSiteManager()
        sm.__bases__ = (reg,) + sm.__bases__
        return

    return orig_installProduct(self, p, locked, hidden, swallowExceptions, 
                               reinstall, forceProfile, omitSnapshots, profile)


orig_upgradeInfo = PQuickInstallerTool.upgradeInfo

def QI_upgradeInfo(self, pid):
    reg = config.getRegistry(pid)
    if reg is not None:
        return {'required': False}

    return orig_upgradeInfo(self, pid)


orig_isProductAvailable = QuickInstallerTool.isProductAvailable


def QI_isProductAvailable(self, pid):
    reg = config.getRegistry(pid)
    if reg is not None:
        return True

    return orig_isProductAvailable(self, pid)


orig_uninstallProducts = QuickInstallerTool.uninstallProducts

def QI_uninstallProducts(self, products=[],
                         cascade=InstalledProduct.default_cascade,
                         reinstall=False, REQUEST=None):
    """ make zpublisher happy """

    changed = False
    curr_sm = getSiteManager()
    bases = list(curr_sm.__bases__)       

    prods = []

    for pid in products:
        reg = config.getRegistry(pid)
        if reg is not None:
            if reg in bases:
                changed = True
                bases.remove(reg)
        else:
            prods.append(pid)
        
    if changed:
        curr_sm.__bases__ = tuple(bases)

    if prods:
        orig_uninstallProducts(self, prods, cascade, reinstall, REQUEST)
    elif REQUEST is not None:
        return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])


@config.action
def patchTypesTool():
    logger = logging.getLogger('memphis.controlpanel')
    logger.info("patching QuickInstallerTool to support utility configlets.")

    # configlets list
    PloneControlPanel.listActions = PloneControlPanel_listActions
    
    # addons
    PQuickInstallerTool.upgradeInfo = QI_upgradeInfo
    QuickInstallerTool.isProductAvailable = QI_isProductAvailable
    QuickInstallerTool.installProduct = QI_installProduct
    QuickInstallerTool.uninstallProducts = QI_uninstallProducts
    QuickInstallerTool.listInstalledProducts = QI_listInstalledProducts
    QuickInstallerTool.listInstallableProducts = QI_listInstallableProducts
