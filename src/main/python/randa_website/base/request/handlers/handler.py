#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This file is part of handler"""
import json

import webapp2
from webapp2_extras import jinja2

import bleach
from randa_website.base.request.endpoint import Endpoint
from randa_website.base.request.handlers.jinja_config import update_config
from randa_website.base.utils.utils import pretty_json
from randa_website.site_config import config

__author__ = "john"
__date__ = "9/23/15 9:25 AM"
__email__ = "john@chaosdevs.com"
__version__ = "2.0.1"


class Handler(Endpoint):
    service = None

    def __init__(self, request, response):
        super(Handler, self).__init__(request, response)
        self.template_file = None
        self.template_values = {}

    def get_html_path(self, name):

        path = '{}/release/{}.html'
        if self.request.get('debug', None) or self.app.debug:
            path = '{}/build/{}.html'
        return path.format(name, name)

    @webapp2.cached_property
    def jinja2(self):
        jinja2.default_config = update_config
        return jinja2.get_jinja2(app=self.app)

    @webapp2.cached_property
    def default_jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def send_resp(self, default=False):

        if not self.template_file:
            raise NotImplementedError('Missing template_file')

        jinja = self.jinja2 if not default else self.default_jinja2

        self.template_values['debug'] = self.request.get('debug') == 'true'
        self.template_values['app_url'] = config.app_url

        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'

        self.template_values = {
            'data': bleach.clean(pretty_json(self.template_values))
        }

        rv = jinja.render_template(self.template_file, **self.template_values)

        self.response.write(rv)
