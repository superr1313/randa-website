# encoding: utf-8
import os
import json


class LocalFileReader(object):

    def __init__(self, local_path):
        self.local_path = local_path

    def get_json(self, file_path, return_dict=False):
        js = open(os.path.join(self.local_path, file_path)).read()
        if return_dict:
            return json.loads(js)
        return js

    def read_json(self, file_path):
        js = open(os.path.join(self.local_path, file_path)).read()
        return json.loads(js)
