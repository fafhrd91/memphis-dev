from setuptools import setup, find_packages

requires = [
    'pyramid',
    'WebError',
    'memphis.config',
    'memphis.view',
    'memphis.form',
    'memphis.users',
    ]

setup(name='testapp',
      version='0.0',
      description='testapp',
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      packages=find_packages(),
      zip_safe=False,
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = testapp:main
      """,
      paster_plugins=['pyramid'],
      )
