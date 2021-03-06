""" Setup for memphis.preferences package

$Id: setup.py 11800 2011-01-31 04:36:54Z fafhrd91 $
"""
import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0'


setup(name='memphis.preferences',
      version=version,
      description="",
      long_description=(
          'Detailed Documentation\n' +
          '======================\n'
          + '\n\n' +
          #read('memphis', 'preferences', 'README.txt')
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
      url='http://pypi.python.org/pypi/memphis.preferences/',
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages=find_packages(),
      namespace_packages=['memphis'],
      install_requires = ['setuptools',
                          'zope.schema',
                          'zope.component',
                          'zope.interface',
                          'memphis.view',
                          'memphis.form',
                          'memphis.storage',
                          ],
      extras_require = dict(test=['memphis.storage [test]',
                                  ]),
      include_package_data = True,
      zip_safe = False,
      entry_points = {
        'memphis': ['include = memphis.preferences']
        },
      )
