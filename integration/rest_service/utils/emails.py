from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from time import sleep

def send_async_email(app, msg):
    with app.app_context():
        # block only for testing parallel thread
        for i in range(10, -1, -1):
            sleep(2)
            print('time:', i)
        print('====> sending async')
        app.mail.send(msg)

def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()


    msg = Message(subject, recipients=[to])
    msg.html = render_template('emails/' + template, **kwargs)


    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr