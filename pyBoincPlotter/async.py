#!/usr/bin/env python
"""
This file is part of the py-boinc-plotter,
which provides parsing and plotting of boinc statistics and
badge information.
Copyright (C) 2013 obtitus@gmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
# END LICENCE
from threading import Thread
"""
Thread class with the ability to return a value, example usage:
t = Async(target=lambda x: x + 1, args=(x, )) # thread is auto started
# .. do other tasks
print t.ret # join is called before value is returned
"""
class Async(Thread):
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
    # Same as above but assume target is a generator
    def run(self):
        self._ret = list(self.target(*self.args, **self.kwargs))
