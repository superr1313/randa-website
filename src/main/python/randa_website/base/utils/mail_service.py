# encoding: utf-8

import os
import logging
import time

from google.appengine.api import mail
from google.appengine.ext.webapp import template
from google.appengine.runtime.apiproxy_errors import DeadlineExceededError

from randa_website.site_config import config, constants


class MailService(object):

    @staticmethod
    def send_mail(recipient, subject, template_name, template_values, sender=config.sender, attach=None, bcc=None,
                  cc=None):

        r_path = os.path.dirname(__file__).rsplit('/', 3)[0]
        path = os.path.join(r_path, 'resources/' + template_name)

        logging.info('EMAIL PATH: {}'.format(path))
        html = template.render(path, template_values)
        email = mail.EmailMessage()
        email.sender = sender
        email.to = recipient
        logging.info('to: %s, bcc: %s' % (recipient, bcc))

        if bcc:
            email.bcc = bcc

        if cc:
            email.cc = cc

        email.subject = subject
        email.html = html
        if attach:
            email.attachments = attach  # NOTE: example of attach [('new.csv', out.getvalue())]

        count = 0
        while True:
            if count > 5:
                logging.error('MailService Failed')
                break

            try:
                email.send()
                break
            except DeadlineExceededError:
                count += 1
                time.sleep(count * constants.EXP_RETRY)

    @staticmethod
    def send_text_message(phone, sender, subject, html):
        email = mail.EmailMessage()
        email.sender = sender
        email.to = phone
        email.subject = subject
        email.html = html
        email.send()
