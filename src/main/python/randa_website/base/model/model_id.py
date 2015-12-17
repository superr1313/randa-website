# encoding: utf-8

""" NDB Base Model class to handle Models that use allocated ID's instead of string ids

"""
from randa_website.base.model.model import Model


class ModelID(Model):

    @classmethod
    def post_dict(cls, data, parent=None):

        first, last = cls.allocate_ids(1, parent=parent)
        return cls._create(first, data, parent)
