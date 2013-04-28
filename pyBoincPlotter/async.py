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
