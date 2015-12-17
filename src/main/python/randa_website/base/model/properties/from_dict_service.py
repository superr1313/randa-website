# encoding: utf-8
import logging
from main import DEBUG
from google.appengine.ext import ndb
from google.appengine.ext.ndb import BlobKey
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from randa_website.base.py_bcrypt import bcrypt
from randa_website.base.request.exceptions.response_exception import ResponseException
from randa_website.site_config import constants

IGNORE_TYPES = (ndb.ComputedProperty, ndb.GenericProperty, ndb.UserProperty)
FALSY = ('false', 'inactive', 0)
TRUTHY = ('true', 'active', 1)
INVALID = 'INVALID'
NOT_FOUND = 'NOT_FOUND'
FROM_IGNORE_KEYS = ['created', 'updated']
PASSWORD = 'password'
EMAIL = 'email'


def validate_from(data, prop):
    key = prop._code_name
    value = data.get(key, NOT_FOUND)
    if value is NOT_FOUND or key in FROM_IGNORE_KEYS or type(prop) in IGNORE_TYPES:
        return False
    return True


def from_geo(value):
    if not isinstance(value, dict):
        return INVALID

    lat = value.get('lat') or value.get('latitude')
    lon = value.get('lon') or value.get('longitude')
    return ndb.GeoPt(lat, lon)


def from_blob_key(value):
    if not value:
        return INVALID
    return BlobKey(value)


def from_key(prop, value):
    if prop._repeated:
        return _from_key_repeated(value)
    return _parse_key(value)


def _from_key_repeated(value):
    keys = value
    if not isinstance(value, list):
        keys = [value]
    key_list = [_parse_key(key) for key in keys]
    return filter(None, key_list)


def _parse_key(value):
    if not value:
        return None
    key = value
    if isinstance(value, dict):
        key = value.get('id')
    try:
        return ndb.Key(urlsafe=key)
    except ProtocolBufferDecodeError:
        error = constants.KEY_NOT_FOUND.format(key)
        if DEBUG:
            raise ResponseException(error)

        logging.error(error)
        return None


def _set_password(value):
    if not constants.PASSWORD_MIN <= len(value) <= constants.PASSWORD_MAX:
        raise ResponseException(constants.PASSWORD, status_int=409)
    return bcrypt.hashpw(value, bcrypt.gensalt())


def _from_string_repeated(values):
    if not values:
        return []
    if not isinstance(values, list):
        values = [values]
    values = filter(None, values)
    return sorted(values, key=lambda item: item.lower())


def from_string(value, prop):

    if prop._repeated:
        return _from_string_repeated(value)

    if not value:
        return ''

    name = prop._code_name
    if name == PASSWORD:
        return _set_password(value)
    elif name == EMAIL:
        return value.lower()
    return value


def from_datetimes(value, prop_type):

    if type(value) in constants.DATE_TYPES:
        return value

    if type(value) not in constants.BASE_STRING_TYPES:
        return None

    # if prop_type == ndb.DateProperty:
    #     return isodate.parse_date(value)
    # elif prop_type == ndb.DateTimeProperty:
    #     return isodate.parse_datetime(value).replace(tzinfo=None)
    # elif prop_type == ndb.TimeProperty:
    #     return isodate.parse_time(value).replace(tzinfo=None)


def _parse_structured(value, prop):
    if not isinstance(value, dict):
        return None

    sub_entity = prop._modelclass()
    return sub_entity.from_dict(value)


def _from_structured_repeated(dicts, prop):
    if not isinstance(dicts, list):
        dicts = [dicts]

    sub_entities = [_parse_structured(each, prop) for each in dicts]
    return filter(None, sub_entities)


def from_structured(value, prop):
    if prop._repeated:
        return _from_structured_repeated(value, prop)

    return _parse_structured(value, prop)


def _parse_repeated_numbers(numbers, modifier):
    values = [_parse_number(each, modifier) for each in numbers]
    return filter(None, values)


def _parse_number(value, modifier):
    if value is None:
        return None
    if isinstance(value, constants.BASE_STRING_TYPES):
        if not value:
            return None
        value = value.replace(',', '')

    return modifier(value)


def from_int(value, prop):
    if prop._repeated:
        return _parse_repeated_numbers(value, int)
    return _parse_number(value, int)


def from_float(value, prop):
    if prop._repeated:
        return _parse_repeated_numbers(value, int)
    return _parse_number(value, float)


def from_boolean(value):
    if isinstance(value, constants.BASE_STRING_TYPES):
        value = value.lower()
        if value in FALSY:
            value = False
        elif value in TRUTHY:
            value = True
    return value
