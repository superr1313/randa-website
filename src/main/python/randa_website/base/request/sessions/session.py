
# encoding: utf-8

import logging
import webapp2
from webapp2_extras import sessions
from randa_website.base.request.crud import CRUD
from webapp2_extras.appengine import sessions_ndb


class SessionEndpoint(CRUD):

    user = None

    def __init__(self, request, response):

        super(SessionEndpoint, self).__init__(request, response)

        self.set_user()

    def set_user(self):
        session_user = self.session.get('user', None)
        if session_user:
            self.user = session_user
            logging.info('CURRENT LOGGED IN USER {}'.format(session_user.email))

    def set_service(self):

        if self.service:
            self.service = self.service(
                kind=self.kind,
                json=self.json,
                entity=self.entity,
                parent=self.parent,
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

