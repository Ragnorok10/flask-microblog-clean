# This will be a simple helper function that sends e-mails

#imports
from flask_mail import Message
from app import mail #imports mail instance form __init__.py

#asynchronous imports
from threading import Thread

#Blueprint imports
from flask import current_app

#Asynchronous functions

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

#email function:

def send_email(subject, sender, recipients, text_body, html_body,
               attachments=None, sync=False):
    msg = Message(subject, sender=sender, recipients=recipients) #this serves as a generic template
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email,
               args=(current_app._get_current_object(), msg)).start()
    
