# encoding: utf-8
from google.appengine.ext import ndb

from main import app
from randa_website.base.request.decorators import required_login
from randa_website.base.request.exceptions.response_exception import ResponseException
from randa_website.base.request.sessions.session import SessionEndpoint
from randa_website.base.utils.task_queue_service import add_task


@app.route('/api/v1/search/upload/([^/]+)')
class UpdateSearchDocs(SessionEndpoint):

    @required_login
    def get(self, kind):

        add_task(
            self.request.path,
            'POST',
            payload={}
        )
        return {'started': 'son'}

    @staticmethod
    def post(kind):

        try:
            cls = ndb.Model._kind_map[kind]

            return cls.quick_put()

        except KeyError as e:
            raise ResponseException(repr(e))
