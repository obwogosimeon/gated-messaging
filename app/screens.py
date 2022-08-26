from __future__ import absolute_import

import os

from flask import current_app

from .jobs import post_whatsapp_reply
from .models import WhatsAppSession, WhatsAppMessage
from . import db


def handle_session(session, phone_number_id):
    next_screen = session.next_screen
    print(session.phone_number)

    if session.next_screen:
        if next_screen == 'verify_house_number':
            post_whatsapp_reply(phone_number_id, verify_house_number(), session.phone_number)
        else:
            post_whatsapp_reply(phone_number_id, verify_house_number_failed(), session.phone_number)
    else:
        # update session
        session.next_screen = 'verify_house_number'
        db.session.add(session)
        db.session.commit()

        post_whatsapp_reply(phone_number_id, welcome_screen(), session.phone_number)


def get_session(phone_number, message, data_schema):
    session = WhatsAppSession.query.filter_by(phone_number=phone_number).first()

    if not session:
        kwargs = {
            'phone_number': phone_number,
            'session_data': message
        }

        try:
            whatsapp_message = WhatsAppMessage(**data_schema)
            new_session = WhatsAppSession(**kwargs)

            db.session.add(new_session)
            db.session.add(whatsapp_message)
            db.session.commit()

            return new_session
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e, exc_info=True)
            return False
    else:
        return session


# actual screens
def welcome_screen():
    return "Welcome to Gated\nPlease enter your house number e.g. JMH-001K:"


def verify_house_number():
    return os.getenv('STATEMENT_SAMPLE')


def verify_house_number_failed():
    return "House information not found. Please check and try again.\nPlease enter your house number e.g. JMH-001K:"
