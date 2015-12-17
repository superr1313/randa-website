# encoding: utf-8
from datetime import datetime, date, time

import os
from google.appengine.api.app_identity import get_application_id

from main import DEBUG

BASE_FILE_PATH = os.path.dirname(__file__)

ADMIN_DEV = 'http://admin-dot-dev.{}.appspot.com:{}'
ADMIN = '{}://admin-dot-{}.appspot.com'
APP_DEV = 'http://localhost:{}'
APP = '{}://{}.appspot.com'
SCHEME = os.getenv('wsgi.url_scheme')
APP_ID = get_application_id()


class Constants(object):
    # HTTP methods
    GET = 'GET'
    PUT = 'PUT'
    POST = 'POST'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'

    TRUE = True  # used to not break stupid pep8 and ndb queries
    FALSE = False  # used to not break stupid pep8 and ndb queries

    MILES_25 = 40233.6  # in meters
    LIMIT = 200
    FETCH_LIMIT = 10000
    COUNT_LIMIT = 1000000

    EXP_RETRY = 2  # exponential back off start amount
    MAX_ERROR_RETRY = 5
    SEARCH_RETRY = 10

    # queue constants
    DEFAULT_QUEUE = 'default'
    ONE_TRY_QUEUE = 'one-try'
    SHARD_KEY_TEMPLATE = 'shard-{}-{:d}'

    # date constants
    NORMAL_DATE = '%m/%d/%y'  # 5/1/14
    PRETTY_DATE = '%a, %b %d, %Y'  # Thu, Jul 03, 2014
    SHORT_DT = '%h %d %I:%M:%S %p'  # Jul 03 10:50:18 PM

    # error constants
    PASSWORD_MIN = 4
    PASSWORD_MAX = 20
    PASSWORD = 'password must be between 4 and 12 characters'
    KEY_NOT_FOUND = 'invalid key: {}'

    DATE_TYPES = (date, datetime, time)
    SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)
    BASE_STRING_TYPES = (basestring, str, unicode)
    JSON_HEADERS = {'Content-Type': 'application/json; charset=UTF-8'}

    # ugly routes crap
    R_PARENT = '([^/]+)'
    ROUTE = '?([^/]*)'

    DEFAULT_REPORT_TPL = 'en/general-done-mapper.html'

    if DEBUG:
        pass


class Config():
    dev_email = 'john.walker.dev@gmail.com'
    devs = ['john.walker.dev@gmail.com']
    site_emails = ['shammond@purqz.com', 'john.walker.dev@gmail.com']
    sender = 'customerservice@purqz.com'
    pdf_client_id = "95f41ba524f3f4ff2bc53bff9a7ad64d"
    pdf_client = "purqz"

    def __init__(self):

        self.app_url = self.get_app_url()
        self.admin_url = self.get_admin_url()

    def get_admin_url(self):
        if self.is_dev():
            return ADMIN_DEV.format(APP_ID, self.port)
        return ADMIN.format(SCHEME, APP_ID)

    def get_app_url(self):
        if self.is_dev():
            return APP_DEV.format(self.port)
        return APP.format(SCHEME, APP_ID)

    @staticmethod
    def is_dev():
        return os.getenv('SERVER_SOFTWARE').startswith('Dev') is True

    @property
    def port(self):
        return os.getenv('SERVER_PORT')


config = Config()
constants = Constants()
