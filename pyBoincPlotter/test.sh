nosetests --with-coverage --cover-html --cover-html-dir test/cover/ --cover-package=pyBoincPlotter* test/

if [ $# -eq 1 ]
then
    ./boinccmd.py
    ./browser.py
    ./plot/deadline.py 
    ./plot/jobLog.py
    ./plot/credits.py
    ./plot/dailyTransfer.py
fi
