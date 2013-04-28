from distutils.core import setup
import pyBoincPlotter.config as config

setup(
    name='pyBoincPlotter',
    version=config.__version__,
    author=config.appAuthor,
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
