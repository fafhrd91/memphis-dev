##############################################################################
#
# Copyright (c) 2001 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Type registration tool """
from warnings import warn

from zope import interface

from Acquisition import aq_parent, Implicit
from AccessControl.class_init import InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager

from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.Expression import Expression
from Products.CMFCore.exceptions import AccessControl_Unauthorized
from Products.CMFCore.interfaces import IAction, ITypeInformation
from Products.CMFCore.permissions import View, ManagePortal
from Products.CMFCore.utils import _checkPermission, getToolByName


class TypeInformation(ActionProviderBase, Implicit):
    """ Base class for information about a content type."""
    interface.implements(IAction, ITypeInformation)

    security = ClassSecurityInfo()

    title = ''
    description = ''
    i18n_domain = ''
    content_meta_type = ''
    icon_expr = ''
    add_view_expr = ''
    immediate_view = ''
    filter_content_types = True
    allowed_content_types = ()
    allow_discussion = False
    global_allow = True
    link_target = ''

    def __init__(self, id, **kw):
        self.id = id
        self._actions = ()
        self._aliases = {}

        if not kw:
            return

        kw = kw.copy()  # Get a modifiable dict.

        if (not kw.has_key('content_meta_type')
            and kw.has_key('meta_type')):
            kw['content_meta_type'] = kw['meta_type']

        if 'content_icon' in kw or 'icon' in kw:
            if 'icon' in kw:
                kw['content_icon'] = kw['icon']
                warn('TypeInformation got a deprecated argument icon.'
                     'Support for the icon argument will be removed in '
                     'CMF 2.4. Please use the icon_expr argument instead.',
                     DeprecationWarning, stacklevel=2)
            else:
                warn('TypeInformation got a deprecated argument content_icon.'
                     'Support for the content_icon argument will be removed in '
                     'CMF 2.4. Please use the icon_expr argument instead.',
                     DeprecationWarning, stacklevel=2)

            if 'icon_expr' not in kw:
                kw['icon_expr'] = 'string:${portal_url}/%s' % kw['content_icon']

        for key, val in kw.items():
            self._setPropValue(key, val)

        actions = kw.get( 'actions', () )
        for action in actions:
            self.addAction(
                  id=action['id']
                , name=action['title']
                , action=action['action']
                , condition=action.get('condition')
                , permission=action.get( 'permissions', () )
                , category=action.get('category', 'object')
                , visible=action.get('visible', True)
                , icon_expr=action.get('icon_expr', '')
                , link_target=action.get('link_target', '')
                )

        self.setMethodAliases(kw.get('aliases', {}))

    #
    #   Accessors
    #
    security.declareProtected(View, 'Title')
    def Title(self):
        return self.title or self.id

    security.declareProtected(View, 'Description')
    def Description(self):
        return self.description

    security.declareProtected(View, 'Metatype')
    def Metatype(self):
        return self.content_meta_type

    security.declarePrivate('getIconExprObject')
    def getIconExprObject(self):
        return getattr(self, 'icon_expr_object', None)

    security.declarePublic('allowType')
    def allowType( self, contentType ):
        if not self.filter_content_types:
            ti = self.getTypeInfo( contentType )
            if ti is None or ti.globalAllow():
                return 1

        #If a type is enabled to filter and no content_types are allowed
        if not self.allowed_content_types:
            return 0

        if contentType in self.allowed_content_types:
            return 1

        return 0

    security.declarePublic('getId')
    def getId(self):
        return self.id

    security.declarePublic('allowDiscussion')
    def allowDiscussion( self ):
        return self.allow_discussion

    security.declarePublic('globalAllow')
    def globalAllow(self):
        return self.global_allow

    security.declarePublic('listActions')
    def listActions(self, info=None, object=None):
        return self._actions

    def create(id, *args, **kw):
        raise NotImplemented

    def isConstructionAllowed(self, container):
        return True

    def _constructInstance(self, container, id, *args, **kw):
        instance = self.create(*args, **kw)
        instance._setId(id)
        rval = container._setObject(id, instance)
        newid = isinstance(rval, basestring) and rval or id
        obj = container._getOb(newid)
        return obj

    security.declarePublic('constructInstance')
    def constructInstance(self, container, id, *args, **kw):
        if not self.isConstructionAllowed(container):
            raise AccessControl_Unauthorized('Cannot create %s' % self.getId())

        return self._constructInstance(container, id, *args, **kw)

    security.declareProtected(ManagePortal, 'getMethodAliases')
    def getMethodAliases(self):
        aliases = self._aliases
        # for aliases created with CMF 1.5.0beta
        for key, method_id in aliases.items():
            if isinstance(method_id, tuple):
                aliases[key] = method_id[0]
                self._p_changed = True
        return aliases.copy()

    security.declareProtected(ManagePortal, 'setMethodAliases')
    def setMethodAliases(self, aliases):
        _dict = {}
        for k, v in aliases.items():
            v = v.strip()
            if v:
                _dict[ k.strip() ] = v
        if not getattr(self, '_aliases', None) == _dict:
            self._aliases = _dict
            return True
        else:
            return False

    security.declarePublic('queryMethodID')
    def queryMethodID(self, alias, default=None, context=None):
        aliases = self._aliases
        method_id = aliases.get(alias, default)
        # for aliases created with CMF 1.5.0beta
        if isinstance(method_id, tuple):
            method_id = method_id[0]
        return method_id
    
    security.declarePrivate('_checkWorkflowAllowed')
    def _checkWorkflowAllowed(self, container):
        wtool = getToolByName(self, 'portal_workflow', None)
        if wtool is None:
            return True
        
        type_id = self.id
        workflows = wtool.getWorkflowsFor(type_id)
        for workflow in workflows:
            # DCWorkflow workflows define an instance creation guard
            guard = getattr(workflow, 'allowCreate', None)

            if guard is None:
                continue

            if not guard(container, type_id):
                return False
        
        return True        

    #
    #   'IAction' interface methods
    #
    security.declarePrivate('getInfoData')
    def getInfoData(self):
        lazy_keys = ['available', 'allowed']
        lazy_map = {}

        lazy_map['id'] = self.id
        lazy_map['category'] = 'folder/add'
        lazy_map['title'] = self.title
        lazy_map['description'] = self.description
        if self.add_view_expr:
            lazy_map['url'] = self.add_view_expr_object
            lazy_keys.append('url')
        else:
            lazy_map['url'] = ''
        if self.icon_expr:
            lazy_map['icon'] = self.icon_expr_object
            lazy_keys.append('icon')
        else:
            lazy_map['icon'] = ''
        lazy_map['link_target'] = self.link_target or None
        lazy_map['visible'] = True
        lazy_map['available'] = self._checkAvailable
        lazy_map['allowed'] = self._checkAllowed

        return (lazy_map, lazy_keys)

    def _setPropValue(self, id, value):
        if hasattr(object, 'aq_base'):
            raise ValueError('Invalid property value: wrapped object')

        if isinstance(value, list):
            value = tuple(value)

        setattr(self, id, value)

        if id.endswith('_expr'):
            attr = '%s_object' % id
            if value:
                setattr(self, attr, Expression(value))
            elif hasattr(self, attr):
                delattr(self, attr)

    def _checkAvailable(self, ec):
        return ec.contexts['folder'].getTypeInfo().allowType(self.id)

    def _checkAllowed(self, ec):
        container = ec.contexts['folder']
        if not _checkPermission(self.permission, container):
            return False
        return self.isConstructionAllowed(container)

    # compatibility
    def getPhysicalPath(self):
        return ('',)


InitializeClass(TypeInformation)
