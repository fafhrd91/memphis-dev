import os, sys
from setuptools import setup, find_packages

VERSION = '0.2'

setup(name='memphis.content',
      version=VERSION,
      description='Memphis content framework',
      long_description="",
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        ],
      author='Nikolay Kim',
      author_email='fafhrd91@gmail.com',
      url='http://pypi.python.org/pypi/memphis.content/',
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
      ],
      extras_require = dict(
        test=['memphis.config [test]'],
        zope=['Zope2',
              'ZODB3',
              'Products.CMFCore',
              'Products.CMFPlone',
              'zope.dublincore',
              'zope.publisher',
              'plone.app.content',
              'memphis.view [zope]',
              ]
        ),
      entry_points = {
        'memphis': ['grokker = memphis.content.meta',
                    'package = memphis.content'],
        }
      )
