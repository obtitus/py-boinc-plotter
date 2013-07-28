
# This file is part of the py-boinc-plotter,
# which provides parsing and plotting of boinc statistics and
# badge information.
# Copyright (C) 2013 obtitus@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# END LICENCE
import os
import re
import datetime
import logging
logger = logging.getLogger('boinc.util')

from math import log10

unit = {12: 'T',
        9: 'G',
        6: 'M',
        3: 'k',
        0: '',        
        -3: 'm',
        -6: 'mu',
        -9: 'n',
        -12: 'p',
        -15: 'f',
        -18: 'a',
        -21: 'z'}

def engineeringUnit(n):
    try:
        x = int(log10(abs(n))//3)*3
    except ValueError:
        x = 0
    try:
        u = unit[x]
    except KeyError:
        x = 0
    return x, unit[x]

def fmtSi(n):
    scale, si = engineeringUnit(n)
    return '{:.3g} {}'.format(n/10**scale, si)

def fmtNumber(x, fmt='.0f'):
    """ Formats large numbers
    """
    #return locale.format(fmt, x)
    fmt = '{:,%s}' % fmt
    return fmt.format(x).replace(',', ' ')

def timedeltaToStr(timedelta):
    """
    Removes the millisecond part of a timedelta string conversion
    """
    timedelta = str(timedelta)
    ix = timedelta.find('.')
    if ix != -1:
        timedelta = timedelta[:ix]
    return timedelta

def strToTimedelta(string):
    if string != None:
        return datetime.timedelta(seconds=float(string))
    else:
        return None

def getLocalFiles(boincDir, name='', extension='.xml'):
    """ Call with name='statistics', extension='.xml'
    for an iterator giving (mindmodeling.org, statistics_mindmodeling.org.xml)
    or with name='job_log', extension='.txt'
    for an iterator gving (mindmodeling.org, job_log_mindmodeling.org.txt)
    """
    if not(os.path.exists(boincDir)):
        logger.error('Could not find boinc dir "%s"', boincDir)
        return ;

    reg_exp = '{0}_(\S*){1}'.format(name, extension)
    logger.debug(reg_exp)
    reg_exp = re.compile(reg_exp)    
    for f in os.listdir(boincDir):
        reg = re.match(reg_exp, f)
        if reg:
            project = reg.group(1)
            filename = os.path.join(boincDir, f)
            yield project, filename

def diffMonths(date1, date2):
    return (date2.year - date1.year)*12 + (date2.month - date1.month)
