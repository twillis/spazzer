import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()


requires = ['repoze.bfg',
            'mutagen',
            'sqlalchemy',
            'alchemyextra',
            'zope.sqlalchemy',
            "Paste>=1.7.2",
            "PasteDeploy>=1.3.3",
            "PasteScript>=1.7.3"]

setup(name = 'spazzer',
      version = '0.0',
      description = 'spazzer',
      long_description = README + '\n\n' + CHANGES,
      classifiers = [
        "Programming Language :: Python",
        "Framework :: BFG",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author = 'Thomas G. Willis',
      author_email = 'tom.willis@gmail.com',
      url = '',
      keywords = 'web wsgi bfg',
      packages = find_packages(),
      include_package_data = True,
      zip_safe = False,
      install_requires = requires,
      tests_require = requires,
      test_suite = "spazzer",
      entry_points = """\
      [paste.app_factory]
      app = spazzer.web.run:app

      [paste.paster_command]
      spazzer-scan = spazzer.collection.scanner:ScannerCommand

      [paste.paster_create_template]
      spazzer-instance = spazzer.config:InstanceTemplate
      """,
      scripts = ["scripts/spazzer"]
      )
