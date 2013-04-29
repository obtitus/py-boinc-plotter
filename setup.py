from distutils.core import setup

__version_info__ = (0, 2, 0)
__version__ = '.'.join(map(str, __version_info__))
appName = 'pyBoincPlotter'
appAuthor = 'obtitus'                   # [at] gmail.com
with open('pyBoincPlotter/version.py', 'w') as f:
    f.write("""__version_info__ = {0}
__version__ = "{1}"
appName = "{2}"
appAuthor = "{3}"
""".format(__version_info__, __version__, appName, appAuthor))

setup(
    name='pyBoincPlotter',
    version=__version__,
    author=appAuthor,
    author_email='obtitus@gmail.com',
    packages=['pyBoincPlotter'],
    scripts=['bin/py-boinc-plotter','bin/py-boinc-change-prefs'],
    url='http://pypi.python.org/pypi/pyBoincPlotter/',
    license='LICENSE.txt',
    description='Provides parsing and plotting of boinc statistics and badge information.',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests",
        "keyring",
        "matplotlib",
        "numpy",
        "PIL",
        "beautifulsoup4",
        "appdirs"
    ],
)
