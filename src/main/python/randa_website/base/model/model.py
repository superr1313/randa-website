# encoding: utf-8

import logging
from google.appengine.ext import ndb
from google.appengine.api import search

from randa_website.base.model.base import BaseModel


class Model(BaseModel):

    updated = ndb.DateTimeProperty(auto_now=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    status = ndb.BooleanProperty(default=True)
    created_by = ndb.StringProperty()
    updated_by = ndb.StringProperty()

    @classmethod
    def _post_delete_hook(cls, key, future):

        if not cls.INDEX:
            return

        index = search.Index(cls.INDEX)

        doc_id = key.urlsafe()
        index.delete(doc_id)
        logging.info('removed search doc for {}'.format(cls.get_kind()))

    @classmethod
    def quick_put(cls):
        entities = cls.query().fetch()
        ndb.put_multi(entities)
        return {'kind': cls.get_kind(), 'count': len(entities)}
