# encoding: utf-8
from datetime import datetime
import logging
from google.appengine.ext import ndb
from google.appengine.api import search
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from randa_website.base.request.exceptions.response_exception import ResponseException
from randa_website.site_config import constants


# noinspection PyUnusedLocal
class Search(object):

    def __init__(self, kind, search_query, search_orders=None, cursor=None, limit=constants.LIMIT, **kwargs):
        """ Build search.Query for app engine Full Text Search

        response is search object
            cursor: web safe cursor,
            number_found: total number available
            count: number returned

        Args:
            kind: App Engine ndb.Model kind
            search_query: raw string to search index
            search_orders: [**{expression, direction[, default_value]}]
                **kwargs dict - convert this to search.SortExpression
            limit: QueryOptions limit - defaults to 200
            cursor: pagination cursor, if none start at beginning

        Raises:
            ResponseException: error message and status_int written to response
        """

        self.kind = kind
        self.search_orders = search_orders
        self.limit = limit
        self.cursor = None
        self.search_query = search_query
        self.dir_map = {
            'asc': search.SortExpression.ASCENDING,
            'desc': search.SortExpression.DESCENDING
        }

        self.set_cursor(cursor)
        logging.info('search query: {} kind: {}'.format(self.search_query, self.kind.get_kind()))

    def set_cursor(self, cursor):
        if cursor:
            self.cursor = search.Cursor(web_safe_string=cursor)
        else:
            self.cursor = search.Cursor()

    def get_index(self):
        return search.Index(name=self.kind.INDEX)

    @staticmethod
    def get_keys(results):

        keys = []
        for result in results:
            try:
                key = ndb.Key(urlsafe=result.doc_id)
                keys.append(key)
            except ProtocolBufferDecodeError:
                pass
        logging.info('number keys: {}'.format(len(keys)))
        return keys

    def simple_search(self):

        index = self.get_index()
        results = index.search(self.search_query)
        keys = self.get_keys(results)
        entities = ndb.get_multi(keys)
        entities = filter(None, entities)
        logging.info('number entities: {}'.format(len(entities)))
        return entities

    def parse_results(self, results):
        next_cursor = results.cursor
        safe_cursor = ''
        if next_cursor:
            safe_cursor = next_cursor.web_safe_string

        number_found = results.number_found

        keys = self.get_keys(results)
        items = ndb.get_multi(keys)
        entities = filter(None, items)

        self.delete_invalid_docs(entities, items, keys)

        logging.info('number entities: {}'.format(len(entities)))
        json_resp = self.kind.json_list(entities)

        return json_resp, safe_cursor, number_found, len(json_resp)

    def search(self):

        query_options = self.build_query_options()
        query = search.Query(query_string=self.search_query, options=query_options)
        logging.info('options: {}'.format(repr(query_options)))
        results = self.do_search(query)
        return self.parse_results(results)

    def build_query_options(self):
        sort_options = self.build_search_orders()

        query_options = search.QueryOptions(
            limit=self.limit,
            ids_only=True,
            cursor=self.cursor,
            sort_options=sort_options
        )
        return query_options

    def build_search_orders(self):
        sort_options = search.SortOptions(expressions=[])
        if self.search_orders:
            for kwarg in self.search_orders:

                direction = kwarg.get('direction', None)
                if direction:
                    kwarg['direction'] = self.dir_map[direction]
                else:
                    kwarg['direction'] = self.dir_map['asc']

                # default value needs to be valid date, stupid. set created and updated by default
                if kwarg.get('expression', None) in ['created', 'updated']:
                    kwarg['default_value'] = datetime(1999, 01, 01)

                sort_expression = search.SortExpression(**kwarg)
                sort_options.expressions.append(sort_expression)
        return sort_options

    def do_search(self, query):

        results = []
        index = self.get_index()
        i = 1
        while True:
            try:
                results = index.search(query)
                if i > 1:
                    logging.info('search i: {}'.format(i))

            except search.Error, e:
                logging.warning('search retries: {}'.format(i))
                logging.error('search error: {}'.format(e.message))
                if i > 8:
                    break
                else:
                    i += 1
                    continue

            break

        return results

    def delete_invalid_docs(self, entities, items, original_keys):

        if len(entities) == len(items):
            return True

        entity_keys = [entity.key for entity in entities]

        diff = list(set(original_keys) - set(entity_keys))
        if not diff:
            return True

        index = self.get_index()
        doc_ids = [key.urlsafe() for key in diff]
        index.delete(doc_ids)
        logging.info('keys deleted: {}'.format(len(doc_ids)))

    # legacy code, might be useful so keep around
    def get_results(self):
        index = self.get_index()
        return index.search(self.search_query)

    @ndb.tasklet
    def get_entities_async(self, kind=None):
        self.kind = kind or self.kind
        if not self.kind:
            raise ResponseException('missing kind in get entities search doc')

        results = self.get_results()
        keys = self.get_keys(results)
        entities = yield ndb.get_multi_async(keys)
        raise ndb.Return(entities)
