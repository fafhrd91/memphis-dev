import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0'


setup(name='memphis.form',
      version=version,
      description="This is fork of z3c.form library.",
      long_description=(
          'Detailed Documentation\n' +
          '======================\n'
          + '\n\n' +
          read('memphis', 'form', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI'],
      author='Nikolay Kim',
      author_email='fafhrd91@gmail.com',
      url='http://pypi.python.org/pypi/memphis.form/',
      license='ZPL 2.1',
      packages=find_packages(),
      namespace_packages=['memphis'],
      install_requires = ['setuptools',
                          'lxml',
                          'pyramid',
                          'chameleon',
                          'memphis.view',
                          'memphis.config',
                          'zope.event',
                          'zope.schema',
                          'zope.component',
                          'zope.interface',
                          'zope.configuration',
                          'zope.contenttype',
                          'zope.i18n',
                          'zope.lifecycleevent',
                          ],
      extras_require = dict(test=['memphis.view [test]']),
      include_package_data = True,
      zip_safe = False,
      entry_points = {
        'memphis': ['include = memphis.form']
        }
      )
