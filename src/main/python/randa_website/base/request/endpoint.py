# encoding: utf-8
import json
import logging
from google.appengine.ext import ndb
import webapp2
from datetime import datetime, time
from randa_website.base.request.base import Base
from randa_website.base.request.decorators import log_duration
from randa_website.base.request.service import Service
from randa_website.base.utils.task_queue_service import add_task
from randa_website.base.utils.times import from_timestamp
from randa_website.base.utils.utils import pretty_json
from randa_website.site_config import constants

JSON_METHODS = ('PUT', 'POST', 'PATCH', 'OPTIONS')
JSON_TYPES = (dict, list, tuple)


class Endpoint(Base):

    service = Service
    kind = None
    json = None
    pretty = None
    to_stamp = None
    from_stamp = None
    sending_file = None
    args = []
    ref = None
    ref_property = None

    def __init__(self, request, response):

        super(Endpoint, self).__init__(request, response)
        self.query = self.request.get('query', None)
        self.parse_json()
        self.parse_stamps()
        self.set_ref()

    def set_service(self):

        """ Injects a service into the endpoint handler

        One kwarg to inject
        endpoint -- self
        """

        if self.service:
            self.service = self.service(
                json=self.json,
                google_user=self.google_user,
                endpoint=self
            )

    def parse_json(self):

        if self.request.method not in JSON_METHODS:
            return None

        body = self.request.body

        try:
            self.json = json.loads(body)

            log = pretty_json(self.json)
            logging.info('body: {}'.format(log))
            self.created_by()

        except ValueError:
            logging.info('body: {}'.format(body))
            pass

    def parse_stamps(self):
        from_str = self.request.get('from', None)
        to = self.request.get('to', None)
        if (to, from_str) == (None, None):
            return
        self.from_stamp = datetime.combine(from_timestamp(from_str), time.min)
        self.to_stamp = datetime.combine(from_timestamp(to), time.max)

    def dispatch(self):
        resp = None
        try:
            try:
                self.set_service()
            except Exception:
                logging.warning("SET SERVICE FAILED")
            resp = webapp2.RequestHandler.dispatch(self)
        finally:
            self.format_resp(resp)

    @log_duration('format-resp')
    def format_resp(self, resp):

        if self.sending_file or hasattr(self, 'template_file'):
            return

        if not isinstance(resp, list):
            resp = resp or {}

        self.response.headers['Content-Type'] = 'application/json'
        if self.headers:
            self.response.headers.update(self.headers)

        if isinstance(resp, basestring):
            self.response.headers['Content-Type'] = 'text/plain'
            write = resp

        elif isinstance(resp, JSON_TYPES):
            if type(resp) == tuple:
                resp = dict(
                    results=resp[0],
                    cursor=resp[1],
                    found=resp[2],
                    count=resp[3]
                )

            if self.pretty:
                write = pretty_json(resp)
            else:
                write = json.dumps(resp)

        else:
            error = {'error': 'format response type failure'}
            write = json.dumps(error)
            logging.exception(error['error'])

        req_time = str((datetime.today() - self.start_time))
        logging.info('{} {}'.format(req_time, write))
        self.response.out.write(write)

    def send_file(self, data, content_type, file_name):
        self.sending_file = True
        self.response.headers['content-type'] = content_type
        self.response.headers['cache-control'] = 'no-cache'
        self.response.headers['accept-ranges'] = 'none'
        self.response.headers['content-disposition'] = 'attachment; filename={}'.format(file_name)

        self.response.out.write(data)

    def created_by(self, is_updated=False):

        """ Get current user's email for ndb.Model created_by property on POST calls

        If self.json is not a dict, return silently

        If a endpoint has a session and a user is logged in then
          self.user will be ndb.Model with property email

        If endpoint does not have a session then it could have self.google_user
          via app engine Users api. Also use email.

        Args:
            self.user: ndb.Model User
            self.google_user: dict
        Returns:
            Injects created_by as a string of the email into self.json.
            If not, 'system' is injected
        Raises:
            Will fail silently and inject 'system'
        """
        if not isinstance(self.json, dict):
            return
        if self.request.method == constants.PUT:
            is_updated = True

        created_by = 'system'
        if hasattr(self, 'user'):
            if self.user:
                created_by = self.user.email

        elif hasattr(self, 'google_user'):
            if self.google_user:
                created_by = self.google_user.get('email', 'system')

        key = 'created_by'
        if is_updated:
            key = 'updated_by'
        logging.info('{} is {}'.format(key, created_by))
        self.json[key] = created_by

    def set_ref(self):
        ref = self.request.get('ref', None)
        if not ref:
            return
        ref_key = ndb.Key(urlsafe=ref)
        self.ref_property = self.request.get('ref_property', None)
        self.ref = ref_key.get()

    def set_args(self):
        args = self.request.route_args
        self.args = []
        if args and len(args):
            for arg in args:
                if arg:
                    self.args.append(arg)

        logging.info('args: {} - {} - {}'.format(self.args, len(self.args), self.request.route.regex.groups))

    def cursor_task(self, data, queue=constants.ONE_TRY_QUEUE):
        add_task(
            self.request.path,
            constants.POST,
            payload=data,
            queue=queue
        )
