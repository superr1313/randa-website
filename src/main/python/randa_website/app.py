#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This file is part of randa-website"""

from randa_website.base.request.handlers.handler import Handler
from main import app

__author__ = "john"
__date__ = "10/5/15 3:30 PM"
__email__ = "john@chaosdevs.com"
__version__ = "2.0.1"


@app.route('^/$')
class AppHandler(Handler):
    def get(self):
        self.template_file = 'index.html'
        self.send_resp()
