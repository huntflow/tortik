# -*- coding: utf-8 -*-

import time
from tornado.web import HTTPError
from tortik.logger import tortik_log


class AsyncGroup(object):
    """
    Grouping of several async requests and final callback in such way, that final callback is invoked after the last
     request is finished.
    """

    def __init__(self, finish_cb, log=None, name=None):
        self.counter = 0
        self.finished = False
        self.finish_cb = finish_cb
        self.log_fun = log if log is not None else tortik_log.debug
        self.name = name

        self.start_time = time.time()
        self.finish_time = None

        if self.name is not None:
            self.log_name = '{0} group'.format(self.name)
        else:
            self.log_name = 'group'

    def _log(self, msg, *args, **kw):
        self.log_fun(self.log_name + ": " + msg, *args, **kw)

    def finish(self):
        if not self.finished:
            self.finish_time = time.time()
            self._log('done in %.2fms', (self.finish_time - self.start_time)*1000.)
            self.finished = True

            try:
                self.finish_cb()
            finally:
                # prevent possible cycle references
                self.finish_cb = None

    def try_finish(self):
        if self.counter == 0:
            self.finish()

    def _inc(self):
        assert(not self.finished)
        self.counter += 1

    def _dec(self):
        self.counter -= 1
        self._log('%s requests pending', self.counter)

    def add(self, intermediate_cb):
        self._inc()

        def wrapper(*args, **kwargs):
            if not self.finished:
                try:
                    self._dec()
                    intermediate_cb(*args, **kwargs)
                except HTTPError:
                    raise
                except Exception:
                    self.try_finish()
                    raise
                else:
                    self.try_finish()
            else:
                self._log('Ignoring response because of already finished group')

        return wrapper

    def add_empty_cb(self):
        self._inc()

        def wrapper(*args, **kwargs):
            self._dec()
            self.try_finish()

        return wrapper
