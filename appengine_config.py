#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   User: john
#   Date: 5/27/15
#   Time: 12:23 AM
#

"""
    Use darth to setup the third-party packages folder
"""

import sys

import darth


darth.add('libs')
darth.add('src/main/python')

reload(sys)
sys.setdefaultencoding("utf8")




# def webapp_add_wsgi_middleware(app):
#     from google.appengine.ext.appstats import recording

# app = recording.appstats_wsgi_middleware(app)
# return app
