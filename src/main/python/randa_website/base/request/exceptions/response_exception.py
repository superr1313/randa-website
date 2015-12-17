# encoding: utf-8


class ResponseException(Exception):
    def __init__(self, message, status_int=500, *args, **kwargs):
        super(ResponseException, self).__init__(*args, **kwargs)
        self.message = message
        self.status_int = status_int