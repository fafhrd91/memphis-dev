import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'WebError',
    'repoze.who',
    'memphis.config',
    'memphis.view',
    'memphis.form',
    'memphis.users',
    'memphis.storage',
    'memphis.controlpanel',
    'memphis.contenttype',
    'memphis.mail',
    'memphis.preferences',
    'memphis.staging',
    ]

setup(name='testapp',
      version='0.0',
      description='testapp',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pylons pyramid',
      packages=find_packages('src'),
      package_dir = {'':'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires = requires,
      tests_require= requires,
      test_suite="testapp",
      entry_points = """\
      [paste.app_factory]
      main = testapp:main
      """,
      paster_plugins=['pyramid'],
      )
