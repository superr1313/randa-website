# encoding: utf-8
from google.appengine.ext import ndb
from randa_website.base.model.properties.timedelta_prop import TimeDeltaProperty


def get_parent(entity, props_to_key):
    parent_key = entity.key.parent()
    if not parent_key:
        return None
    parent = parent_key.get()
    if parent is None:
        return None

    if 'parent' in props_to_key:
        return parent_key.urlsafe()
    return parent.to_dict()


def parse_key(name, key, key_props):
    if name in key_props:
        return key.urlsafe()

    entity = key.get()
    if entity:
        return entity.to_dict()
    return None


def to_datetimes(prop_type, value):
    # if prop_type == ndb.DateProperty:
    #     return isodate.date_isoformat(value)
    #
    # elif prop_type == ndb.TimeProperty:
    #     return isodate.time_isoformat(value)
    #
    # elif prop_type == ndb.DateTimeProperty:
    #     return isodate.datetime_isoformat(value) + 'Z'
    return None
    # elif prop_type == TimeDeltaProperty: return str(value)


def to_user(google_user):
    return dict(
        id=google_user.user_id(),
        email=google_user.email(),
        name=google_user.nickname()
    )


def to_geo(value):
    return dict(
        lat=value.lat,
        lon=value.lon,
        latitude=value.lat,
        longitude=value.lon,
        geo=str(value)
    )
