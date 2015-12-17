# -*- coding: utf-8 -*-

DEBUG = True

from randa_website.base import email_logger
from randa_website.base import micro_webapp2
from randa_website.module_urls import app_urls
from randa_website.base.wsgi_setup import domain_middleware

app_config = {
    'webapp2_extras.sessions': {
        'secret_key': '3265163f-ccf1-4f2b-812c-fb4c9dbd9ef5'
    }
}

app = micro_webapp2.WSGIApplication(debug=DEBUG, config=app_config)

application = domain_middleware([
    ('.*', app, app_urls)
])

email_logger.register_logger(['randa.nunn@mokimobility.com'])
