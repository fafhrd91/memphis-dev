""" Setup for memphis.storage package

$Id: setup.py 11801 2011-01-31 06:25:03Z fafhrd91 $
"""
import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0'


setup(name='memphis.storage',
      version=version,
      description="",
      long_description=(
          'Detailed Documentation\n' +
          '======================\n'
          + '\n\n' +
          read('memphis', 'storage', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Repoze Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent'],
      author='Nikolay Kim',
      author_email='fafhrd91@gmail.com',
      url='http://pypi.python.org/pypi/memphis.storage/',
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
                          'memphis.config',
                          ],
      entry_points = {
        'memphis': ['include = memphis.storage']
        },
      include_package_data = True,
      zip_safe = False)
