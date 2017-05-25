#!/usr/bin/env python
# coding: utf-8

#===================================================
import sendgrid
from sendgrid.helpers.mail import *
#===================================================

class SGMail(object):

    def __init__(self, apikey, from_email, to_email):
        self.sg = sendgrid.SendGridAPIClient(apikey=apikey)
        self.from_email = Email(from_email)
        self.to_email = Email(to_email)

    def send_mail(self, subject, plain_content, type='text/plain'):
        content = Content(type, plain_content)
        mail = Mail(self.from_email, subject, self.to_email, content)
        response = self.sg.client.mail.send.post(request_body=mail.get())
        return response.status_code == 202
