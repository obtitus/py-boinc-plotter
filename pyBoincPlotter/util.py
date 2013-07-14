import os
import re
import datetime
import logging
logger = logging.getLogger('boinc.util')

def fmtNumber(x, fmt=''):
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
