# encoding: utf-8

import calendar
from datetime import datetime, timedelta
import time as os_time
from randa_website.site_config import constants


def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month / 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return datetime(year, month, day)


def get_dt(dt=datetime.now(), **kwargs):
    return dt + timedelta(**kwargs)


def get_timestamp():
    return int(round(os_time.time() * 1000))


def dt_to_timestamp(dt, **kwargs):
    dt = get_dt(dt=dt, **kwargs)
    return int(round(os_time.mktime(dt.timetuple()) * 1000))


def from_timestamp(ts):
    return datetime.fromtimestamp(int(ts) / 1000.0)


def normal_date(dt=datetime.now()):
    if not dt:
        return 'N/A'
    return dt.strftime(constants.NORMAL_DATE)


def normal_from_str(date_string):
    if not date_string:
        return 'N/A'
    return datetime.strptime(date_string, constants.DEFAULT_DATE).strftime(constants.NORMAL_DATE)
