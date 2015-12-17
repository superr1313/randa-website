# coding=utf-8

from datetime import datetime
from google.appengine.ext import ndb
import logging
from common.decorator import decorator


def time_log(name):
    ctx = ndb.get_context()
    start_time = ctx._cache.get('start_time')
    td = None
    if start_time:
        td = datetime.now() - start_time
        logging.debug('-- {} TIME: {}'.format(name, td))
    return td


def time_me(name):
    @decorator
    def _time_me(fn, self, *args, **kwargs):
        resp = fn(self, *args, **kwargs)
        time_log(name)
        return resp

    return _time_me
