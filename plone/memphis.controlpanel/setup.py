import os, sys
from setuptools import setup, find_packages

VERSION = '0.1'

setup(name='memphis.controlpanel',
      version=VERSION,
      description='Plone alternative control panel system',
      long_description="",
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        ],
      author='Nikolay Kim',
      author_email='fafhrd91@gmail.com',
      url='http://pypi.python.org/pypi/memphis.controlpanel/',
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages=find_packages(),
      namespace_packages=['memphis'],
      zip_safe=False,
      include_package_data=True,
      install_requires = [
        'setuptools',
        'memphis.config',
        'memphis.view',
        'memphis.form',
        'zope.component',
      ],
      extras_require = dict(
        test=['memphis.config [test]'],
        zope=['Zope2',
              'ZODB3',
              'AccessControl',
              'Products.CMFCore',
              'Products.CMFPlone',
              'memphis.view [zope]',
              ]
        ),
      entry_points = {
        'memphis': ['package = memphis.controlpanel'],
        }
      )
