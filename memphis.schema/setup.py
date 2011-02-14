import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0'


setup(name='memphis.schema',
      version=version,
      description="",
      long_description=(
          'Detailed Documentation\n' +
          '======================\n'
          + '\n\n' +
          #read('memphis', 'schema', 'README.txt')
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
      url='http://pypi.python.org/pypi/memphis.schema/',
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages=find_packages(),
      namespace_packages=['memphis'],
      install_requires = ['setuptools',
                          'sqlalchemy',
                          'sqlalchemy_migrate',
                          'zope.schema',
                          'zope.interface',
                          'pyramid',
                          'memphis.view',
                          'memphis.form',
                          'memphis.storage',
                          'z3c.schema',
                          'plone.supermodel',
                          'rwproperty',
                          ],
      extras_require = dict(test=['memphis.storage [test]',
                                  ]),
      include_package_data = True,
      zip_safe = False,
      entry_points = {
        'memphis': ['include = memphis.schema']
        }
      )
