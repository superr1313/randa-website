# encoding: utf-8

import webapp2


class WSGIApplication(webapp2.WSGIApplication):

    allowed_methods = frozenset((
        'GET', 'POST', 'HEAD', 'OPTIONS',
        'DELETE', 'TRACE', 'PATCH', 'PUT'
    ))

    def __init__(self, *args, **kwargs):
        super(WSGIApplication, self).__init__(*args, **kwargs)
        self.endpoint_base = None
        self.endpoints = {}

    def route(self, *args, **kwargs):
        def wrapper(func):
            full_route = (args[0], '{}.{}'.format(func.__module__, func.__name__))
            # print 'full route', full_route
            self.router.add(full_route)
            return func

        return wrapper

    # def path(self, *args, **kwargs):
    #     def wrapper(func):
    #         name = func.__name__
    #         endpoint = self.endpoints.get('name')
    #         if endpoint:
    #             pass
    #         else:
    #             self.endpoints['name'] = {}
    #
    #         print 'func', func
    #         print 'args', args
    #         print 'kr', kwargs
    #         print 'end', self.endpoint_base
    #         self.endpoint_base = kwargs['name']
    #         return func
    #
    #     return wrapper