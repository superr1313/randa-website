# encoding: utf-8

import logging
from google.appengine.ext import ndb
from randa_website.base.request.endpoint import Endpoint
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from randa_website.base.request.exceptions.response_exception import ResponseException


class CRUD(Endpoint):

    json_parent_key = False

    entity = None
    parent = None
    parent_key = None
    validate = True
    is_parent_crud = False

    def __init__(self, request, response):

        super(CRUD, self).__init__(request, response)
        self.cursor = self.request.get('cursor', None)

        self.set_is_parent()
        self.set_args()
        self.set_keys_from_args()
        self.validate_parent()

    def do_get(self, **kwargs):

        """ handles crud for GET of model endpoints.

        Scenarios to handle.
        1. self.current_key -- ndb.Key, if set it is the key of the current entity to get.
            if is_parent_crud and nested groups match self.args, then still single entity get

        2. if groups > len(self.args) then self.current_key is the parent
            and should do a ancestor query. Validate parents in this case

        3. no current key -- default to return full list of entities (used in admin pages)

        4. self.query -- query param do search

        instance -- return non json entity
        order -- query orders to apply

        if not instance then no return,
        function calls BaseService.format_resp, serializes writes json response
        """

        if self.query is not None:
            resp = self.service.get_query_search(self.query, **kwargs)

        elif self.entity:
            resp = self.service.id_get(**kwargs)

        elif self.parent:
            resp = self.service.ancestor_query(**kwargs)

        else:
            resp = self.service.all_get(**kwargs)

        return resp

    def do_post(self, **kwargs):
        kwargs['parent'] = self.parent_key
        return self.service.post_dict(self.json, **kwargs)

    def do_put(self, **kwargs):
        return self.service.put_dict(self.json, **kwargs)

    def do_delete(self):
        return self.kind.delete_from_key(self.entity.key)

    def set_keys_from_args(self):

        """ Sets self.entity_key and self.parent_key if either are valid

        Scenarios to handle
        1. If the last id on the route is available and valid then converted to ndb.Key - self.entity_key
        2. If multiple groups in route and second to last is valid then converted to ndb.Key - self.parent_key

        self.entity_key -- the current entity key for the crud request
        self.parent_key -- the current entities parent
        """

        groups = self.request.route.regex.groups
        if not self.kind:
            return

        if groups == len(self.args):
            try:
                entity_key = ndb.Key(urlsafe=self.args[-1])
                self.entity = entity_key.get()
                # logging.info('entity_key: {}'.format(self.entity.key))
                # if self.entity:
                #     logging.info('entity_key: {}'.format(self.entity.key))

            except ProtocolBufferDecodeError:
                logging.warning('ProtocolBufferDecodeError, not a valid ndb.Key: {}'.format(self.args[-1]))
            except TypeError:
                logging.warning('Incorrect padding, not a valid ndb.Key: {}'.format(self.args[-1]))
            except Exception as e:
                logging.warning('Uncaught: {}'.format(e))

        if self.is_parent_crud:
            if self.request.route_args[-2]:
                self.parent = ndb.Key(urlsafe=self.request.route_args[-2]).get()
                self.parent_key = self.parent.key

            elif not self.entity:
                raise ResponseException('route is missing key parameters')

        if self.json_parent_key and self.json:
            parent_key = self.json['parent']['id']
            if parent_key:
                self.parent = ndb.Key(urlsafe=parent_key).get()
                self.parent_key = self.parent.key

        # logging.info('parent_key: {}'.format(self.parent_key))

    def validate_parent(self):

        if not self.is_parent_crud:
            return

        if not self.validate:
            return

        is_valid = True
        if not self.parent:
            is_valid = False

        if not is_valid:
            raise ResponseException('Invalid Parents Key: {}'.format(self.args))

    def set_is_parent(self):
        """ if a url path has more groups than 1 it is a nested entity key relationship """

        if self.request.route.regex.groups > 1:
            self.is_parent_crud = True

    def set_service(self):

        """ Injects a service in the endpoint if defined

        Five kwargs to inject
        kind     -- entity kind
        json     -- self.json from the request body
        entity   -- the current injected entity
        parent   -- the current injected parent if self.is_parent_crud
        request  -- normal webapp2 request object
        """

        if self.service:
            self.service = self.service(
                kind=self.kind,
                json=self.json,
                entity=self.entity,
                parent=self.parent,
                google_user=self.google_user,
                endpoint=self
            )
