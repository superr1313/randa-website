# encoding: utf-8
import webapp2
from webapp2_extras import jinja2

from randa_website.base.request.handlers.jinja_config import update_config


class JinjaService(object):

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        jinja2.default_config = update_config
        return jinja2.get_jinja2(app=webapp2.WSGIApplication.active_instance)

    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        return self.jinja2.render_template(_template, **context)
