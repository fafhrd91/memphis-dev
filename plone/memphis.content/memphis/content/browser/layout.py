""" 

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
from memphis import view, content
from Products.CMFCore.interfaces import ISiteRoot, ITypeInformation
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


view.registerLayout(
    '', ISiteRoot,
    klass = view.ZopeLayout,
    template = ViewPageTemplateFile(
        view.path('memphis.content:templates/layout-contentcore.pt'))
)


view.registerLayout(
    '', ITypeInformation,
    klass = view.ZopeLayout,
    template = ViewPageTemplateFile(
        view.path('memphis.content:templates/layout-content.pt'))
)


view.registerLayout(
    'body', content.IContent,
    klass = view.ZopeLayout,
    template = ViewPageTemplateFile(
        view.path('memphis.content:templates/layout-body.pt'))
)
