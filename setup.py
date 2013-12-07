from distutils.core import setup

__version_info__ = (0, 4, 4)
__version__ = '.'.join(map(str, __version_info__))
appName = 'pyBoincPlotter'
appAuthor = 'obtitus'                   # [at] gmail.com
with open('pyBoincPlotter/version.py', 'w') as f:
    f.write("""# This file is autogenerated by setup.py, do not edit.
__version_info__ = {0}
__version__ = "{1}"
appName = "{2}"
appAuthor = "{3}"
""".format(__version_info__, __version__, appName, appAuthor))

if __name__ == '__main__':
    setup(
        name='pyBoincPlotter',
        version=__version__,
        author=appAuthor,
        author_email='obtitus@gmail.com',
        packages=['pyBoincPlotter', 'pyBoincPlotter.plot', 'pyBoincPlotter.test'],
        scripts=['bin/py-boinc-plotter','bin/py-boinc-change-prefs'],
        url='http://pypi.python.org/pypi/pyBoincPlotter/',
        license='LICENSE.txt',
        description='Provides parsing and plotting of boinc statistics and badge information.',
        long_description=open('README.txt').read(),
        install_requires=[
            "requests",
            "keyring",
            "numpy",
            "matplotlib",
            "PIL",
            "lxml",
            "beautifulsoup4",
            "appdirs",
            "mako"
        ],
    )
