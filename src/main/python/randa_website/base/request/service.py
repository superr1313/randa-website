# encoding: utf-8
import csv
from cStringIO import StringIO
from randa_website.base.model.base import BaseModel

from randa_website.base.search_doc.search_doc import Search


class Service(object):

    """
    This is a base service, a helper for endpoint processing.
    This should one day have all common injection or crud functions.
    What used to be the dao.
    """

    def __init__(self, *args, **kwargs):
        self.kind = kwargs.get('kind', BaseModel)
        self.json = kwargs.get('json', None)
        self.entity = kwargs.get('entity', None)
        self.parent = kwargs.get('parent', None)
        self.endpoint = kwargs.get('endpoint', None)
        self.session = kwargs.get('session', None)
        self.google_user = kwargs.get('google_user', None)
        if self.session:
            self.user = self.session.get('user', None)

    def get_query_search(self, query, **kwargs):
        kwargs['cursor'] = self.endpoint.cursor
        self.build_search_query()
        searcher = Search(self.kind, self.endpoint.query, **kwargs)
        return searcher.search()

    def build_search_query(self):
        pass

    def id_get(self, **kwargs):
        """ Return entity or to_dict of entity

        Kwargs:
            key: if key is set use to get entity, otherwise return self.entity
            instance: don't to_dict
            silent: don't raise exception
        """
        key = kwargs.get('key')
        if key:
            self.entity = self.kind.get_entity(key, **kwargs)
        return self.get_resp(self.entity, **kwargs)

    def ancestor_query(self, **kwargs):
        """ Query entities that belong to one root entity group using self.parent.key

        Kwargs:
            filters, query, orders -- apply to ancestor query
            instance -- return entities
            return dict list
        """
        entities = self.kind.ancestor_query(self.parent.key, **kwargs)
        return self.get_resp(entities, **kwargs)

    def all_get(self, **kwargs):
        entities = self.kind.all_get(**kwargs)
        return self.get_resp(entities, **kwargs)

    def post_dict(self, data, **kwargs):
        """ Creates new entity.

        Args:
            data: dict of properties to set onto new instance of self.kind
        """
        parent_key = kwargs.get('parent')
        entity = self.kind.post_dict(data, parent=parent_key)
        return self.get_resp(entity, **kwargs)

    def put_dict(self, data, **kwargs):
        """ Updates existing entity.

        Will ignore all attributes of entity that is not within data dictionary
        Args:
            data: dict of properties to update with.
        """
        entity = self.kind.put_dict(data)
        return self.get_resp(entity, **kwargs)

    def get_resp(self, incoming, **kwargs):
        key_props = kwargs.get('key_props')
        instance = kwargs.get('instance')
        resp = None
        if instance:
            return incoming

        if isinstance(incoming, list):
            resp = self.kind.json_list(incoming, key_props=key_props)
        elif isinstance(incoming, BaseModel):
            resp = incoming.to_dict(key_props=key_props)

        return resp

    @staticmethod
    def get_csv_output(headers, data_set):
        output = StringIO()
        writer = csv.DictWriter(output, headers)
        writer.writeheader()
        writer.writerows(data_set)
        return output.getvalue()
