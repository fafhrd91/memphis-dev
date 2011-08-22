""" Setup for memphis.app package """
import sys, os
from setuptools import setup, find_packages

version='0.1dev'

setup(name='memphis.mail',
      version=version,
      description="",
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
      url='http://pypi.python.org/pypi/memphis.mail/',
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages = find_packages(),
      namespace_packages = ['memphis'],
      install_requires = [
        'setuptools',
        'memphis.config',
        'repoze.sendmail'
        ],
      include_package_data = True,
      zip_safe = False,
      entry_points = {
        'memphis': ['package = memphis.mail'],
        },
      )
