# encoding: utf-8
import json
import logging

from google.appengine.ext import ndb


from google.appengine.api.taskqueue import Task
from google.appengine.api.taskqueue import Queue
from randa_website.base.utils.utils import pretty_json
from randa_website.site_config import constants


class TaskQueueService(object):

    def __init__(self):
        self.queue_names_dict = {}

    def _get_queue(self, name):
        if not self.queue_names_dict.get(name):
            self.queue_names_dict[name] = []
        return self.queue_names_dict[name]

    def push_task(self, url, method, payload=None, queue=constants.DEFAULT_QUEUE, eta=None, countdown=None, log=True):

        queue_list = self._get_queue(queue)

        if isinstance(payload, dict):
            payload = pretty_json(payload)

        task = Task(
            url=url,
            method=method,
            payload=payload,
            eta=eta,
            countdown=countdown
        )
        if log:
            self._log_task(task, queue)
        queue_list.append(task)

    def add_tasks(self):

        for queue_name, tasks in self.queue_names_dict.items():
            queue = Queue(queue_name)
            self._enqueue(queue, tasks)

        self.queue_names_dict = {}

    @ndb.transactional(retries=5)
    def _enqueue(self, queue, tasks):
        queue.add(tasks)

    @staticmethod
    def _log_task(task, queue_name):
        data = {
            'url': task.url,
            'method': task.method,
            'queue': queue_name,
            'eta': str(task.eta_posix),
            'payload': json.loads(task.payload)
        }
        logging.info('task: {}'.format(pretty_json(data)))


def add_task(url, method, payload=None, params=None, queue=constants.DEFAULT_QUEUE, eta=None, countdown=None):

    if isinstance(payload, dict):
        payload = pretty_json(payload)
        logging.info('payload: {}'.format(payload))

    if queue is None:
        queue = 'default'

    task = Task(
        url=url,
        method=method,
        payload=payload,
        params=params,
        eta=eta,
        countdown=countdown
    )

    if params:
        logging.info('params: {}'.format(task.extract_params()))

    task.add(queue_name=queue)
