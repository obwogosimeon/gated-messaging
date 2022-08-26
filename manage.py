from __future__ import absolute_import

import logging
import os
import requests

from logging.handlers import RotatingFileHandler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from dotenv import load_dotenv
from flask import Flask, current_app
from flask_apscheduler import APScheduler as _BaseAPScheduler
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate, MigrateCommand
from flask_script import Server, Manager
from datetime import datetime

from app import db
from app.models import SMS

load_dotenv()

bcrypt = Bcrypt()
mail = Mail()

_basedir = os.path.abspath(os.path.dirname(__file__))


class APScheduler(_BaseAPScheduler):
    def run_job(self, id, jobstore=None):
        with self.app.app_context():
            super().run_job(id=id, jobstore=jobstore)


def do_scheduled_jobs():
    with application.app_context():
        headers = {'Content-Type': 'application/json'}
        payload = {}

        sms_messages = SMS.query.filter(SMS.send_at <= datetime.now(), SMS.sent == False).all()
        for sms_message in sms_messages:
            sms_url = os.getenv('UWAZI_SMS_URL')
            token = os.getenv('UWAZI_TOKEN')
            sender_id = os.getenv('UWAZI_SENDER_ID')
            phone = sms_message.phone[1:]
            text = sms_message.message

            payload = {

            }

            url = f'{sms_url}?token={token}&phone={phone}&senderID={sender_id}&text={text}'

            response = requests.request("GET", url, headers=headers, data=payload)

            if response.ok:
                current_app.logger.error(response.json(), exc_info=True)
                current_app.logger.error(response.text, exc_info=True)

                sms_message.sent = True
                db.session.add(sms_message)
                db.session.commit()
            else:
                print('sms send error')


def configure_app(flask_app):
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_DATABASE = os.getenv("DB_DATABASE")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    RUN_DEBUG = os.getenv("DEBUG")

    flask_app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    flask_app.config['DEBUG'] = RUN_DEBUG
    flask_app.config['MAIL_SERVER'] = os.getenv('MAIL_HOST')
    flask_app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    flask_app.config['MAIL_USE_SSL'] = False
    flask_app.config['MAIL_USERNAME'] = os.getenv('MAIL_USER')
    flask_app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    flask_app.config['MAIL_DEBUG'] = 0
    flask_app.config['LOGFILE'] = '{}/logs/log.log'.format(_basedir)

    flask_app.config['SCHEDULER_JOBSTORES'] = {
        'default': SQLAlchemyJobStore(
            url=flask_app.config['SQLALCHEMY_DATABASE_URI']
        ),
    }

    flask_app.config['SCHEDULER_API_ENABLED'] = False
    flask_app.config['JOBS'] = [
        {
            'id': 'c2322554-7c8a-4540-99e9-2ded1ac4f75f',
            'func': do_scheduled_jobs,
            'trigger': 'interval',
            'seconds': 30,
            'replace_existing': True
        },
    ]
    flask_app.config['SCHEDULER_EXECUTORS'] = {
        'default': {
            'type': 'threadpool',
            'max_workers': 2
        }
    }
    flask_app.config['SCHEDULER_JOB_DEFAULTS'] = {
        'coalesce': False,
        'max_instances': 1
    }
    flask_app.config['SCHEDULER_TIMEZONE'] = os.getenv('TIME_ZONE')


def initialize_app(flask_app):
    configure_app(flask_app)

    CORS(application)
    bcrypt.init_app(application)
    mail.init_app(application)

    from app.sms import sms
    from app.whatsapp import whatsapp

    application.register_blueprint(sms)
    application.register_blueprint(whatsapp)

    file_handler = RotatingFileHandler(application.config['LOGFILE'], maxBytes=20971520, backupCount=5, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = '%(asctime)s [%(filename)s:%(lineno)d] : %(message)s'
    file_formatter = logging.Formatter(file_format)
    file_handler.setFormatter(file_formatter)
    application.logger.addHandler(file_handler)

    db.init_app(flask_app)

    @application.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,PATCH,POST,DELETE')
        return response

    @application.route('/')
    def api():
        return {'version': 'v1.0', 'title': 'GMS Rest API'}


application = Flask(__name__)
initialize_app(application)

scheduler = APScheduler()
scheduler.init_app(application)
scheduler.start()

db.bcrypt = bcrypt
db.mail = mail
db.scheduler = scheduler
db.application = application

db_manager = Manager(usage='database commands')
migrate = Migrate(application, db)

manager = Manager(application)
manager.add_command("runserver", Server(port=5000))
manager.add_command('db', MigrateCommand)


if __name__ == "__main__":
    application.logger.setLevel(logging.DEBUG)
    manager.run()
