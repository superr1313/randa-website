# encoding: utf-8
import json
import logging
import os
from randa_website.site_config import BASE_FILE_PATH


def pretty_json(_json, is_json=False):
    def dumps(data):
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    if is_json:
        return dumps(json.loads(_json))
    return dumps(_json)


def find(f, seq):
    """Return first item in sequence where f(item) == True."""
    for item in seq:
        if f(item):
            return item


def join_path(path):
    joined = os.path.join(BASE_FILE_PATH, path)
    logging.info('joined', joined)
    return joined


def natural_sort_key(items, key):
    from natsort import natsorted
    from operator import itemgetter

    return natsorted(items, key=lambda x: itemgetter(key)(x).lower())


def multi_key_sort(items, columns):
    from operator import itemgetter

    comparers = [((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in
                 columns]

    def comparer(left, right):
        for fn, multi in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return multi * result
        else:
            return 0

    return sorted(items, cmp=comparer)
