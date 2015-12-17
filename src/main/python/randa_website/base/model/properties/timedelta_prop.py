# encoding: utf-8

from google.appengine.ext import ndb
from datetime import datetime, timedelta


class TimeDeltaProperty(ndb.DateTimeProperty):
    # Use a reference datetime half way between the min and max possible
    # datetimes, so that we can support both +ve and -ve timedeltas
    _ref_datetime = (datetime.max - datetime.min) / 2 + datetime.min

    def _validate(self, value):
        if not isinstance(value, timedelta):
            raise TypeError('expected a datetime.timedelta, got {}'.format(value))

    def _to_base_type(self, value):
        # datetime + timedelta = datetime
        return self._ref_datetime + value

    def _from_base_type(self, value):
        # datetime - datetime = timedelta
        return value - self._ref_datetime