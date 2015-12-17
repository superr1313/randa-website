# encoding: utf-8
import webapp2
from webapp2_extras import sessions
from webapp2_extras.appengine import sessions_ndb

from randa_website.base.request.endpoint import Endpoint


class SimpleSession(Endpoint):
    """

    """
    user = None

    def __init__(self, request, response):

        super(SimpleSession, self).__init__(request, response)

    def set_service(self):

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
            self.set_service()
            # Dispatch the request.
            resp = webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)
            self.format_resp(resp)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session(name='db_session', factory=sessions_ndb.DatastoreSessionFactory)
