================
Py Boinc plotter
================

This project is an alternative to the boinc gui, it does not run boinc! Please see http://boinc.berkeley.edu/ for more information about boinc. This project requires the command line version to be installed, as communication with boinc is done via the boinccmd utility.

It currently outputs information about current tasks running on the local machine, in addition to information from the project webpage.

Currently supported projects:
  * worldcommunitygrid.org (currently mandatory!)
  * wuprop.boinc-af.org (no badge support yet)
  * mindmodeling.org
  * boinc.bakerlab.org (rosetta)
  * www.rechenkraft.net/yoyo (no badge support yet)
Others may work, but these are the ones I have tested. Let me know how it works on other projects! Proper support for badges will be added if I ever get one.

More info
=========
Please have a look at the google code repository code.google.com/p/py-boinc-plotter and/or the wiki with features
code.google.com/p/py-boinc-plotter/wiki/Features

Requirements
============
This project should be viewed as pre-alpha, currently being developed on mac os x 10.7 with python2.7. Other python versions or operating systems may require some modifications. The following libraries are used:
  * python-requests.org/
  * https://pypi.python.org/pypi/keyring
  * matplotlib, numpy (only required for plotting)
  * PIL (only for displaying badges)

Please see the wiki for installation instructions and screenshots.

Author
======
Øystein Bjørndal
