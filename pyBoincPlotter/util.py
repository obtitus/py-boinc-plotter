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
