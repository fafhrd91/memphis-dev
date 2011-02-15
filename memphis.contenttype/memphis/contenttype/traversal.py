""" custom pyramid traversal """
import urllib
from zope import interface
from pyramid.interfaces import ITraverser
from pyramid.interfaces import VH_ROOT_KEY
from pyramid.traversal import traversal_path

from memphis import config

from location import LocationProxy
from interfaces import IRoot, IContainer


class ResourceTreeTraverser(object):
    """ A resource tree traverser that should be used (for speed) when
    every resource in the tree supplies a ``__name__`` and
    ``__parent__`` attribute (ie. every resource in the tree is
    :term:`location` aware) ."""
    interface.implements(ITraverser)
    config.adapts(IRoot)

    VIEW_SELECTOR = '@@'

    def __init__(self, root):
        self.root = root

    def __call__(self, request):
        environ = request.environ

        if 'bfg.routes.matchdict' in environ:
            matchdict = environ['bfg.routes.matchdict']

            path = matchdict.get('traverse', '/')
            if hasattr(path, '__iter__'):
                # this is a *traverse stararg (not a :traverse)
                path = '/'.join([quote_path_segment(x) for x in path]) or '/'

            subpath = matchdict.get('subpath', ())
            if not hasattr(subpath, '__iter__'):
                # this is not a *subpath stararg (just a :subpath)
                subpath = traversal_path(subpath)

        else:
            # this request did not match a route
            subpath = ()
            try:
                path = environ['PATH_INFO'] or '/'
            except KeyError:
                path = '/'

        if VH_ROOT_KEY in environ:
            vroot_path = environ[VH_ROOT_KEY]
            vroot_tuple = traversal_path(vroot_path)
            vpath = vroot_path + path
            vroot_idx = len(vroot_tuple) -1
        else:
            vroot_tuple = ()
            vpath = path
            vroot_idx = -1

        root = self.root
        ob = vroot = root

        if vpath == '/' or (not vpath):
            vpath_tuple = ()
        else:
            i = 0
            view_selector = self.VIEW_SELECTOR
            vpath_tuple = traversal_path(vpath)

            for segment in vpath_tuple:
                if segment[:2] == view_selector:
                    return {'context':ob,
                            'view_name':segment[2:],
                            'subpath':vpath_tuple[i+1:],
                            'traversed':vpath_tuple[:vroot_idx+i+1],
                            'virtual_root':vroot,
                            'virtual_root_path':vroot_tuple,
                            'root':root}

                cont = IContainer(ob, None)
                if cont is None:
                    return {'context':ob,
                            'view_name':segment,
                            'subpath':vpath_tuple[i+1:],
                            'traversed':vpath_tuple[:vroot_idx+i+1],
                            'virtual_root':vroot,
                            'virtual_root_path':vroot_tuple,
                            'root':root}
                else:
                    try:
                        next = LocationProxy(cont[segment], ob, segment)
                    except KeyError:
                        return {'context':ob,
                                'view_name':segment,
                                'subpath':vpath_tuple[i+1:],
                                'traversed':vpath_tuple[:vroot_idx+i+1],
                                'virtual_root':vroot,
                                'virtual_root_path':vroot_tuple,
                                'root':root}
                if i == vroot_idx:
                    vroot = next
                ob = next
                i += 1

        return {'context':ob, 'view_name':u'', 'subpath':subpath,
                'traversed':vpath_tuple, 'virtual_root':vroot,
                'virtual_root_path':vroot_tuple, 'root':root}
