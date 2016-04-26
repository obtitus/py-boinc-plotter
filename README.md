Python project for plotting boinc statistics and current tasks. Please see http://boinc.berkeley.edu/ for more information about boinc, command line version required for certain features.

Uses both the boinc rpc and the command line version to communicate with boinc. Does web crawling on boinc websites for further task information (valid/credits/...), statistics and badges. Please see the [https://code.google.com/p/py-boinc-plotter/wiki/Features features] page for more information

## Motivation ##
  * Updates on request only (not continuously)
  * Tracks task state, making it easier to detect invalidated workunits.
  * Shows remaining time compared to deadline
  * Shows progress towards next badge level
  * Plots many of the boinc output files (job_log, time_stats_log, daily_xfer_history, ...)
  * Command line interface to boinc preferences

# Currently supported projects #
  * worldcommunitygrid.org (badge support)
  * wuprop.boinc-af.org (badge support)
  * www.primegrid.com (badge support)
  * numberfields.asu.edu/NumberFields (badge support)
  * mindmodeling.org
  * www.rechenkraft.net/yoyo
  * boincsimap.org/boincsimap
  * Rosetta@home: boinc.bakerlab.org
  * Climatepredication.net: climateapps2.oerc.ox.ac.uk/cpdnboinc
  * FightMalaria@home: boinc.ucd.ie/fmah/

Others may work, but these are the ones I have tested. Let me know how it works on other projects!

# Requirements #
This project should be viewed as pre-alpha, currently being developed on a mac with python2.7. Other python versions or operating systems may require some modifications. The following libraries are used:

  * python-requests.org/
  * https://pypi.python.org/pypi/keyring
  * matplotlib, numpy (only required for plotting)
  * PIL (only for displaying badges from worldcommunitygrid)
  * beautifullSoup4 with lxml
  * appdirs

# Installation #
There are three options for installing this package, using pip, using setup.py or by simply running the python script.
### From pip ###
The simplest way of installing this software with dependencies is to download the tarball and run:
> pip pyBoincPlotter-<version>.tar.gz
where <version> is the newest version available. The project will be added to pip once it is a bit more stable.

### With setup.py ###
Alternatively the usual "python setup.py install" should do the trick. Though you have to figure out the dependencies our-shelf.

### No install ###
You don't actually need to install this package, simply run:
> python <path>/pyBoincPlotter/boinc.py
instead of "py-boinc-plotter"

# Configuration #
It is important to distinguish between projects attached to boinc and projects attached to py-boinc-plotter, one does not imply the other! py-boinc-plotter only does web crawling on projects you tell it about, using the --add option:

```
   py-boinc-plotter --add wuprop.boinc-af.org
```

You will then be prompted for username (email address), password and userid. Userid is visible on the projects "Your account" page. If you want to change this information simply run the above command again, or edit the configuration file.

For worldcommunitygrid you will need your "Verification Code", you can find your "Verification Code" by going to worldcommunitygrid.org -> My Grid -> My Profile. Note that the password is stored securely by keyring, but the account key is stored as plain text in the configuration file. This does not configure boinc in any way, it simple gives py-boinc-plotter access to statistics on the given website.

To attach new projects to boinc use any of the standard methods, use an account manager, the BOINCManager gui or the command line boinccmd. As a shourtcut, extra command line arguments to py-boinc-plotter is passed to boinccmd, so the following should work:

```
    py-boinc-plotter --add URL --project_attach URL auth
```

The first arguments tells py-boinc-plotter about the given project and the second attaches that project to boinc.

Please see

```
    py-boinc-plotter --help
```

for more options
