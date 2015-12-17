# encoding=utf-8
import logging
from main import admin
from google.appengine.api.search import search
from randa_website.base.request.endpoint import Endpoint
from randa_website.base.utils.task_queue_service import add_task


@admin.route(r'/admin/v1/search/remove/([^/]+)')
class RemoveSearchDocIndex(Endpoint):

    @staticmethod
    def get(index_name):

        add_task(
            '/admin/v1/search/remove/{}'.format(index_name),
            'POST'
        )
        return {'task': 'given'}

    @staticmethod
    def post(index_name):

        doc_index = search.Index(name=index_name)

        counter = 0

        while True:

            if counter > 20000:
                break
            # Get a list of documents populating only the doc_id field and extract the ids.
            document_ids = [document.doc_id
                            for document in doc_index.get_range(ids_only=True)]
            if not document_ids:
                break
            # Delete the documents for the given ids from the Index.
            doc_index.delete(document_ids)

            counter += len(document_ids)

            if not counter % 5:
                logging.info('current ids: {}'.format(counter))

        logging.info('removed: {}'.format(counter))
        return {'status': 'done son', 'total': counter}
