# encoding: utf-8
import uuid
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop

from randa_website.base.model.properties.from_dict_service import INVALID
from randa_website.base.model.properties import to_dict_service, from_dict_service
from randa_website.base.model.properties.timedelta_prop import TimeDeltaProperty
from randa_website.base.request.exceptions.response_exception import ResponseException
from randa_website.site_config import constants

DYNAMIC_PROPS = (
    msgprop.EnumProperty,
    ndb.GeoPtProperty, ndb.KeyProperty,
    ndb.UserProperty, ndb.BlobKeyProperty,
    ndb.StructuredProperty, ndb.LocalStructuredProperty,
    ndb.DateProperty, ndb.DateTimeProperty, ndb.TimeProperty, TimeDeltaProperty
)

STRUCT_PROPS = (ndb.StructuredProperty, ndb.LocalStructuredProperty)
NDB_DATE_TYPES = (ndb.DateProperty, ndb.DateTimeProperty, ndb.TimeProperty, TimeDeltaProperty)
STRING_TYPES = (ndb.StringProperty, ndb.TextProperty, ndb.BlobProperty, basestring, str, unicode)

TO_IGNORE_KEYS = ['password']


# noinspection PyProtectedMember
class BaseModel(ndb.Model):

    __prop = None
    INDEX = None
    REF = None

    def __init__(self, *args, **kwargs):
        super(BaseModel, self).__init__(*args, **kwargs)

    def to_dict(self, key_props=None):
        key_props = key_props or []
        data = super(BaseModel, self).to_dict()
        data.update(self._update_keys(key_props))

        for each in TO_IGNORE_KEYS:
            data.pop(each, None)

        for name, value in data.iteritems():
            self.__prop = self._properties.get(name)
            prop_type = type(self.__prop)
            if prop_type not in DYNAMIC_PROPS:
                continue

            value = self._get_value(prop_type, name, value, key_props)
            data[name] = value

        return data

    def _get_value(self, prop_type, name, non_parsed, key_props):
        if non_parsed is None:
            return None

        if prop_type == ndb.GeoPtProperty:
            parsed = to_dict_service.to_geo(non_parsed)

        elif prop_type == ndb.KeyProperty:
            parsed = self._to_key(name, non_parsed, key_props)

        elif prop_type == ndb.BlobKeyProperty:
            parsed = str(non_parsed)

        elif prop_type in STRUCT_PROPS:
            parsed = self._to_structured(name)

        elif prop_type == ndb.UserProperty:
            parsed = to_dict_service.to_user(non_parsed)

        elif prop_type in NDB_DATE_TYPES:
            parsed = to_dict_service.to_datetimes(prop_type, non_parsed)

        elif prop_type == msgprop.EnumProperty:
            parsed = str(non_parsed)

        else:
            parsed = None

        return parsed

    def _update_keys(self, key_props):
        if not self.key:
            return {}
        data = dict(
            id=self.key.urlsafe(),
            key_id=self.key.id()
        )
        parent = to_dict_service.get_parent(self, key_props)
        if parent:
            data['parent'] = parent
        return data

    def _to_structured(self, name):
        if self.__prop._repeated:
            return [entity.to_dict() for entity in getattr(self, name) if entity]
        else:
            return getattr(self, name).to_dict()

    def _to_key(self, name, key, key_props):
        if self.__prop._repeated:
            return [to_dict_service.parse_key(name, each, key_props) for each in key if each]
        else:
            return to_dict_service.parse_key(name, key, key_props)

    def from_dict(self, data):

        if not data:
            return self

        for key, prop in self._properties.iteritems():
            if not from_dict_service.validate_from(data, prop):
                continue

            incoming_value = data[key]
            self._set_value(incoming_value, prop)

        return self

    def _set_value(self, incoming_value, prop):

        prop_type = type(prop)
        if prop_type == ndb.GeoPtProperty:
            value = from_dict_service.from_geo(incoming_value)

        elif prop_type == ndb.BlobKeyProperty:
            value = from_dict_service.from_blob_key(incoming_value)

        elif prop_type == ndb.KeyProperty:
            value = from_dict_service.from_key(prop, incoming_value)

        elif prop_type in STRING_TYPES:
            value = from_dict_service.from_string(incoming_value, prop)

        elif prop_type in NDB_DATE_TYPES:
            value = from_dict_service.from_datetimes(incoming_value, prop_type)

        elif prop_type in STRUCT_PROPS:
            value = from_dict_service.from_structured(incoming_value, prop)

        elif prop_type == ndb.IntegerProperty:
            value = from_dict_service.from_int(incoming_value, prop)

        elif prop_type == ndb.FloatProperty:
            value = from_dict_service.from_float(incoming_value, prop)

        elif prop_type == ndb.BooleanProperty:
            value = from_dict_service.from_boolean(incoming_value)

        elif prop_type == ndb.JsonProperty:
            value = incoming_value

        elif prop_type == msgprop.EnumProperty:
            value = getattr(prop._enum_type, incoming_value)

        else:
            raise Exception(str(prop))

        if value is not INVALID and value is not None:
            setattr(self, prop._code_name, value)

    @classmethod
    def ancestor_query(cls, ancestor_key, **kwargs):
        query = cls.query(ancestor=ancestor_key)
        return cls._apply_query(query, **kwargs)

    @classmethod
    def get_from_reference(cls, ref, **kwargs):
        ref_property = kwargs.get('ref_property') or cls.REF
        query = cls.query(cls._properties[ref_property] == ref.key)
        return cls._apply_query(query, **kwargs)

    @classmethod
    def all_get(cls, **kwargs):
        """ Query datastore for all entities, applying orders and filters

        filters -- array of tuples (prop_name, operator, value)
        return list of entities or serialized list of entities
        """

        query = cls.query()
        return cls._apply_query(query, **kwargs)

    @classmethod
    def get_entity(cls, key_string, **kwargs):
        """
        Gets an entity by its full key string
        key_string could be the actual key set up in the base service
        :param silent: don't raise exception if silent is True
        :return: model
        """
        key = cls._key_from_request(key_string)
        entity = key.get()
        if entity is None:
            cls._raise_error(constants.KEY_NOT_FOUND.format(key_string), **kwargs)

        return entity

    @classmethod
    def get_from_key(cls, key, **kwargs):
        entity = cls.get_entity(key)
        return entity.to_dict()

    @classmethod
    def post_dict(cls, data, parent=None):
        _id = data.get('id') or str(uuid.uuid4())
        return cls._create(_id, data, parent)

    @classmethod
    def put_dict(cls, data):
        model = cls.get_entity(data['id']).from_dict(data)
        model.put()
        return model

    @classmethod
    def delete_from_key(cls, key_string):
        key = cls._key_from_request(key_string)
        key.delete()
        return {}

    @classmethod
    def json_list(cls, entities, key_props=None):
        array = [entity.to_dict(key_props=key_props) for entity in entities if entity]
        return array

    @classmethod
    def _apply_query(cls, query, **kwargs):
        filters = kwargs.get('filters')
        orders = kwargs.get('orders')
        limit = kwargs.get('limit')
        if filters:
            for each in filters:
                query = cls._add_filter(query, each)

        if orders:
            for each in orders:
                query = query.order(each)

        return query.fetch(limit)

    @classmethod
    def _add_filter(cls, query, query_filter):

        cls_prop, op, value = query_filter
        if op == constants.eql:
            query = query.filter(cls_prop == value)
        elif op == constants.gt:
            query = query.filter(cls_prop > value)
        elif op == constants.gte:
            query = query.filter(cls_prop >= value)
        elif op == constants.lt:
            query = query.filter(cls_prop < value)
        elif op == constants.lte:
            query = query.filter(cls_prop <= value)
        elif op == constants.ne:
            query = query.filter(cls_prop != value)
        return query

    @classmethod
    def _create(cls, _id, data, parent=None):
        parent = cls._key_from_request(parent)

        key_list = [cls.get_kind(), _id]
        if parent:
            key_list = list(parent.flat()) + key_list

        model = cls(key=ndb.Key(flat=key_list))

        model.from_dict(data).put()
        return model

    @staticmethod
    def _key_from_request(key):
        if isinstance(key, constants.BASE_STRING_TYPES):
            return ndb.Key(urlsafe=key)
        return key

    @staticmethod
    def _raise_error(msg, **kwargs):
        if not kwargs.get('silent', False):
            raise ResponseException(msg)

    @classmethod
    def get_kind(cls):
        return cls._get_kind()

    @classmethod
    def clone(cls, entity_to_clone, parent=None):
        new_entity = cls._create(entity_to_clone.key.id(), {}, parent=parent)
        new_entity.from_dict(entity_to_clone.to_dict())
        entity_to_clone.key.delete()
        new_entity.put()
        return new_entity

    @staticmethod
    def build_suggestions(value):
        if not isinstance(value, constants.BASE_STRING_TYPES):
            return ''
        suggestions = []
        for word in value.split():
            prefix = ""
            for letter in word:
                prefix += letter
                suggestions.append(prefix)
        return ' '.join(suggestions)

    def to_currency(self, prop_name):

        prop = getattr(self, prop_name)
        formatted = "${:.2f}".format(float(prop))
        return formatted
