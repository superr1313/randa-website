# encoding: utf-8

import re
import os
import logging
import urlparse
from webapp2 import get_request


def get_compile(string, ignore=False):
    app_id = os.environ['APPLICATION_ID'].split('~')[1]
    server_type = os.environ['SERVER_SOFTWARE']
    if server_type.startswith('Dev'):
        if ignore:
            return re.compile(string)
        app_id = '{}.{}'.format('dev.', app_id)
        return re.compile(string % app_id)

    if ignore:
        return re.compile(string)
    return re.compile(string % app_id)


def domain_middleware(domain_map):
    d_map = get_domain_regex_map(domain_map)

    def middleware(environ, start_response):

        domain = environ['SERVER_NAME']
        if 'admin' not in domain:
            domain += environ["PATH_INFO"]
        for regex, app, urls in d_map:
            # match = regex.match(domain)
            # logging.info('DOMAIN MIDDLEWARE')
            # logging.info('domain: {}'.format(domain))
            # logging.info('regex-pattern: {}'.format(regex.pattern))
            # logging.info('is-match: {}\n'.format(match is not None))

            if regex.match(domain):
                # logging.info('import urls: {}'.format(urls))
                import_handlers(urls)
                return app(environ, start_response)

    return middleware


def get_domain_regex_map(domain_map):
    d_map = []
    for key, value, urls in domain_map:
        if isinstance(key, basestring):
            tup = re.compile('^%s$' % key), value, urls
            # logging.info('regex-pat: {}'.format('^%s$' % key))
        else:
            tup = key, value, urls
        d_map.append(tup)

    return d_map


def import_handlers(handlers):
    for path in handlers:
        parts = path.split('.')
        cls = path.split('.')[-1]
        import_path = '.'.join(parts[0:-1])

        __import__(import_path, fromlist=cls)


def handle_404(request, response, *args):
    logging.error('404 url: {}'.format(request.path_url))
    uri = '/#/404'
    if uri.startswith(('.', '/')):
        request = request or get_request()
        uri = str(urlparse.urljoin(request.url, uri))
    response.headers['Location'] = uri
    response.status = 301
    response.write('sdf')
    return response