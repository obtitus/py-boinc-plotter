import datetime

try:
    import numpy as np
    import pylab as plt
    import matplotlib
    import matplotlib.image as mpimg    
    matplotlib.rc('text', usetex=False)
    plt.ion()

    def timeTicks(x, pos):
        d = datetime.timedelta(seconds=x)
        s = str(d)
        if d.days < 0:
            d = datetime.timedelta(seconds=-x)
            s = '-' + str(d)
        return s
    formatter_timedelta = matplotlib.ticker.FuncFormatter(timeTicks)
except ImportError as e:
    print e
