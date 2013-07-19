#!/usr/bin/env python
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
from threading import Thread
from multiprocessing.pool import ThreadPool
POOL_SIZE = 10

import datetime
datetime.datetime.strptime("", "") # avoids threading bug, see http://bugs.python.org/issue7980 

class Async(Thread):
    """
    Thread class with the ability to return a value, example usage:
    t = Async(target=lambda x: x + 1, args=(x, )) # thread is auto started
    # .. do other tasks
    print t.ret # join is called before value is returned
    """
    def __init__(self, target, *args, **kwargs):
        Thread.__init__(self)#, group=None, target=target, args=(), kwargs={})
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.start()

    def run(self):
        self._ret = self.target(*self.args, **self.kwargs)

    @property
    def ret(self):
        self.join()
        return self._ret

class AsyncGen(Async):
    """ Same as above but assume target is a generator"""
    def run(self):
        self._ret = list(self.target(*self.args, **self.kwargs))

class Pool(ThreadPool):
    """Similar to async_map"""
    def __init__(self, target, *args, **kwargs):
        ThreadPool.__init__(self, processes=POOL_SIZE)
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.map_async()

    def map_async(self):
        self._ret = list()
        for arg in self.args:
            self._ret.append(self.apply_async(func=self.target,
                                              args=(arg, ),
                                              kwds=self.kwargs))
    
    @property
    def ret(self):
        self.close()
        self.join()
        # return self._ret
        get = list()
        for r in self._ret:
            get.append(r.get())
        return get

if __name__ == '__main__':
    from time import sleep

    def foo(item):
        print 'sleeping'
        sleep(10)
        return item

    a = Pool(foo, *range(10))
    #sleep(10)
    print 'Done'
    print a.ret
