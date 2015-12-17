# encoding: utf-8
import csv
import sys
import json
import logging
import traceback
from cStringIO import StringIO
from datetime import datetime

import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import memcache

from randa_website.base.utils.utils import pretty_json
from randa_website.site_config import constants


exec_format = '%(filename)s - %(line_num)s - %(func_name)s - %(message)s'
log_format = '%(module)s.%(funcName)s at %(lineno)d -- %(message)s'
fr = logging.Formatter(log_format)
logging.getLogger().handlers[0].setFormatter(fr)


class Base(webapp2.RequestHandler):

    google_user = None
    debug = False
    internal_debug = True

    def __init__(self, request, response):

        super(Base, self).__init__(request, response)
        self.start_time = datetime.today()
        ctx = ndb.get_context()
        ctx._cache['start_time'] = self.start_time
        self.headers = {}
        self.set_user()
        self.log_name()

    def log_name(self):
        name = '{}.{}.{}'.format(self.__class__.__module__, self.__class__.__name__, self.request.method)
        logging.info(name)

    def set_user(self):
        google_user = users.get_current_user()
        if google_user:
            self.google_user = dict(
                email=google_user.email(),
                name=google_user.nickname(),
                id=google_user.user_id()
            )
            logging.info('google user: {}'.format(google_user.email()))

    def handle_exception(self, exception, debug):

        exc_type, exc_value, exc_traceback = sys.exc_info()
        filename, line_num, func_name, text = traceback.extract_tb(exc_traceback)[-1]
        message = exception.message
        warning = False

        self.response.status_int = 500

        if hasattr(exception, 'status_int'):
            self.response.status_int = exception.status_int

        self.response.status_message = message

        #  409 http status code conflict, meaning the user sent invalid data and should be able to change and resubmit
        if self.response.status_int == 409:
            warning = True

        if warning:
            logging.warning(message)
        else:
            data = self.clean_request_environ()
            data = pretty_json(data)
            logs = locals()
            logs['filename'] = '.'.join(logs['filename'].split('/')[-3:])
            logging.exception(exec_format, logs)

        return {"error": exception.message, 'status': self.response.status, 'status_int': self.response.status_int}

    def validate_task_count(self):

        is_valid = True
        count = self.request.headers.environ.get('HTTP_X_APPENGINE_TASKRETRYCOUNT', None)
        if count is not None:
            task_count = int(count)
            if task_count > 0:
                is_valid = False

        return is_valid

    def clean_request_environ(self):

        import urllib

        environ = self.request.environ

        def parse_cookie(cookies):

            cookies = cookies.split('; ')
            handler = {}

            for cookie in cookies:
                cookie = urllib.unquote(cookie)
                cookie = cookie.split('=')
                if cookie[1].startswith('{') and cookie[1].endswith('}'):
                    handler[cookie[0]] = json.loads(cookie[1])
                else:
                    handler[cookie[0]] = cookie[1]
            return handler

        clean = {}
        for key, value in environ.iteritems():
            if key == 'HTTP_COOKIE':
                clean['HTTP_COOKIE'] = parse_cookie(value)
            elif type(value) not in constants.SIMPLE_TYPES:
                clean[key] = str(value)
            else:
                clean[key] = value
        return clean

    @staticmethod
    def get_csv_output(headers, data_set):
        output = StringIO()
        writer = csv.DictWriter(output, headers)
        writer.writeheader()
        writer.writerows(data_set)
        return output.getvalue()
