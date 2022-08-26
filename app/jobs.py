from __future__ import absolute_import

import os

import requests
from flask import current_app


def post_whatsapp_reply(phone_id, message, msg_from):
    token = os.getenv('WHATSAPP_TOKEN')

    headers = {
        'Content-type': 'application/json'
    }
    url = f"https://graph.facebook.com/v12.0/{phone_id}/messages?access_token={token}"
    data = {
        'messaging_product': 'whatsapp',
        'to': msg_from,
        'text': {
            'body': message
        }
    }

    whatsapp_message_request = requests.post(url, headers=headers, json=data)
    whatsapp_message_json = whatsapp_message_request.json()

    current_app.logger.error(whatsapp_message_json, exc_info=True)
