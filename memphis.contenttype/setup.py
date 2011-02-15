""" Setup for memphis.contenttype package

$Id: setup.py 11635 2011-01-18 07:03:08Z fafhrd91 $
"""
import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0'


setup(name='memphis.contenttype',
      version=version,
      description="",
      long_description=(
          'Detailed Documentation\n' +
          '======================\n'
          + '\n\n' +
          read('memphis', 'contenttype', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Repoze Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI'],
      author='Nikolay Kim',
      author_email='fafhrd91@gmail.com',
      url='http://pypi.python.org/pypi/memphis.contenttype/',
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages=find_packages(),
      namespace_packages=['memphis'],
      install_requires = ['setuptools',
                          'Chameleon',
                          'zope.event',
                          'zope.schema',
                          'zope.component',
                          'zope.interface',
                          'zope.configuration',
                          'pyramid',
                          'memphis.config',
                          'memphis.view',
                          'memphis.form',
                          'memphis.storage',
                          'memphis.schema',
                          'memphis.controlpanel',
                          ],
      extras_require = dict(test=['memphis.config [test]']),
      include_package_data = True,
      zip_safe = False,
      entry_points = {
        'memphis': ['include = memphis.contenttype']
        }
      )
