""" Setup for memphis.container package

$Id: setup.py 4719 2011-02-03 01:47:46Z nikolay $
"""
import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0'


setup(name='memphis.container',
      version=version,
      description="",
      long_description=(
          'Detailed Documentation\n' +
          '======================\n'
          + '\n\n' +
          #read('memphis', 'container', 'README.txt')
          #+ '\n\n' +
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
      url='http://pypi.python.org/pypi/memphis.container/',
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages=find_packages(),
      namespace_packages=['memphis'],
      install_requires = ['setuptools',
                          'martian',
                          'sqlalchemy',
                          'zope.event',
                          'zope.schema',
                          'zope.component',
                          'zope.interface',
                          'zope.lifecycleevent',
                          'memphis.config',
                          'memphis.storage',
                          'memphis.view',
                          ],
      extras_require = dict(test=['memphis.config [test]',
                                  ]),
      entry_points = {
        'memphis': ['include = memphis.container']
        },
      include_package_data = True,
      zip_safe = False)
