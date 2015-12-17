# encoding: utf-8

import logging
import json

from google.appengine.ext.ndb import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.ndb.blobstore import BlobInfo, BlobKey

from randa_website.base.request.endpoint import Endpoint, JSON_METHODS
from randa_website.base.utils.utils import pretty_json


class BlobEndpoint(Endpoint, blobstore_handlers.BlobstoreUploadHandler):
    """

    """
    blob_info = None

    def __init__(self, request, response):
        super(BlobEndpoint, self).__init__(request, response)
        self.set_blob_info()

    def get(self):
        """ Default blob url get.

        Override in child class to send back a different url then endpoint requested from
        :return: blobstore upload url
        """
        return {
            'url': blobstore.create_upload_url(self.request.path)
        }

    def set_blob_info(self):
        uploads = self.get_uploads()
        if uploads:
            self.blob_info = uploads[0]
            logging.info('FILE NAME: {}'.format(self.blob_info.filename))

    def handle_exception(self, exception, debug):
        resp = super(BlobEndpoint, self).handle_exception(exception, debug)
        if self.blob_info:
            logging.info('deleting blob: %s' % self.blob_info.filename)
            self.blob_info.delete()
        return resp

    def parse_json(self):

        if self.request.method not in JSON_METHODS:
            return None

        body = self.request.body

        try:
            self.json = json.loads(body)

            blob_key = self.json.get('blob_key')
            if blob_key:
                self.blob_info = BlobInfo.get(BlobKey(blob_key))

            log = pretty_json(self.json)
            logging.info('body: {}'.format(log))

        except ValueError:
            logging.info('body: {}'.format(body))
