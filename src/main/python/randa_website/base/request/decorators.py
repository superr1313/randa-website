# encoding: utf-8
import logging
from datetime import datetime

from randa_website.base.request.exceptions.response_exception import ResponseException
from decorator import *


def required_login(handler):
    """ Requires that a user be logged in to access the resource """

    def check_login(self, *args, **kwargs):
        session_user = self.session.get('user', None)
        if not session_user:
            raise ResponseException("invalid auth", status_int=401)
        else:
            return handler(self, *args, **kwargs)

    return check_login


def request_keys(keys):
    """ Requires that incoming json have specific property names in post body """

    @decorator
    def _request_keys(fn, self, *args):
        json_keys = self.json.keys()
        for each in keys:
            if each not in json_keys:
                raise ResponseException('keys not in list: %s, %s' % (json_keys, keys))
        return fn(self, *args)

    return _request_keys


def lower_keys(keys):
    """ Performs str.lower() on incoming json body properties """

    @decorator
    def _lower_keys(fn, self, *args):
        prop = None
        try:
            for key in keys:
                prop = self.json[key]
                self.json[key] = prop.lower()
            return fn(self, *args)
        except KeyError:
            raise ResponseException('Property {} not found is post body'.format(prop))
        except AttributeError:
            raise ResponseException('Property {} is not a string'.format(prop))

    return _lower_keys


def optional_keys(keys):
    @decorator
    def _self(fn, self):

        options = []

        for each in keys:
            if each in self.keys:
                options.append(each)
        if not options:
            raise ResponseException('optional keys not in list: %s, %s' % (self.keys, keys))

        return fn(self)

    return _self


def log_duration(name):
    """Decorator that sets time, calls method and then logs the timedelta """

    @decorator
    def _log_duration(fn, self, *args, **kwargs):
        start = datetime.now()
        resp = fn(self, *args, **kwargs)
        logging.debug('-- {} duration : {}'.format(name, str(datetime.now() - start)))
        return resp

    return _log_duration
