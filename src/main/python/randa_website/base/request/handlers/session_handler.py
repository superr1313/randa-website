# encoding: utf-8

import webapp2
from webapp2_extras import sessions
from webapp2_extras.appengine import sessions_ndb
from randa_website.base.request.handlers.handler import Handler


class SessionHandler(Handler):

    def __init__(self, request, response):
        super(SessionHandler, self).__init__(request, response)
        # self.set_service()

    def set_service(self):

        """ Injects a service into the endpoint handler

        One kwarg to inject
        endpoint -- self
        """

        if self.service:
            self.service = self.service(
                json=self.json,
                session=self.session,
                google_user=self.google_user,
                endpoint=self
            )

    @webapp2.cached_property
    def session_store(self):
        return sessions.get_store(request=self.request)

    def dispatch(self):
        resp = None
        try:
            resp = webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)
            self.format_resp(resp)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session(name='db_session', factory=sessions_ndb.DatastoreSessionFactory)
