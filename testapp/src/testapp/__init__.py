import os, threading
from zope import interface
from zope.configuration import xmlconfig
from zope.component import getSiteManager
import pyramid_sqla
from pyramid.interfaces import INewRequest
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from memphis import storage, view
from memphis import config as memphis_config
from memphis.contenttype import root

my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')


def newRequest(request):
    storage.setSession(pyramid_sqla.get_session())


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application. """

    def get_root(request):
        return root.getRoot()

    authentication_policy = AuthTktAuthenticationPolicy('seekrit')
    authorization_policy = ACLAuthorizationPolicy()

    config = Configurator(root_factory=get_root, settings=settings,
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy,
                          session_factory = my_session_factory)
    config.hook_zca()
    config.begin()

    config.add_subscriber(newRequest, INewRequest)

    # load all memphis dependencies
    memphis_config.loadPackage('testapp')

    # start memphis config
    memphis_config.begin()

    # initialize database
    pyramid_sqla.add_engine(settings, prefix='sqlalchemy.')

    # static view
    config.add_static_view('static', 'testapp:static')

    # commit memphis commit
    memphis_config.commit()

    # initialize memphis
    storage.initialize(pyramid_sqla.get_engine(),
                       pyramid_sqla.get_session())

    config.end()
    return config.make_wsgi_app()
