# encoding: utf-8
import random
import string


def to_currency(dictionary, prop_name):
    dictionary[prop_name] = "$%.2f" % float(dictionary.get(prop_name))
    return dictionary


def format_currency(value):
    return "$%.2f" % float(value)


def format_percent(value):
    return "%.2f %%" % float(value)


def get_short_code():
    return ''.join(random.sample(string.uppercase + string.digits, 6))