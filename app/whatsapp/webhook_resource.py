from __future__ import absolute_import

import os

from flask import current_app
from flask_restful import Resource, reqparse, abort

from app.screens import get_session, handle_session


class WebhookResource(Resource):
    def __init__(self):
        super(self.__class__, self).__init__()

    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('hub.mode', required=True, help='mode')
        parser.add_argument('hub.verify_token', required=True, help='verify token')
        parser.add_argument('hub.challenge', required=True, help='challenge')

        args = parser.parse_args()

        mode = args.get('hub.mode')
        token = args.get('hub.verify_token')
        challenge = args.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == os.getenv('VERIFY_TOKEN'):
                return int(challenge), 200
            else:
                return {}, 403
        else:
            return {}, 400

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('object', required=True, help='object')
        parser.add_argument('entry', type=list, location='json', required=True, help='entry')

        args = parser.parse_args()

        try:
            entry = args['entry']
            entry_0 = args['entry'][0]

            changes = entry_0['changes']
            changes_0 = changes[0]

            if entry and changes and changes_0 and changes_0['value']['messages'] and changes_0['value']['messages'][0]:
                phone_number_id = changes_0['value']['metadata']['phone_number_id']
                message_from = changes_0['value']['messages'][0]['from']
                message_body = changes_0['value']['messages'][0]['text']['body']

                # kwargs for logging
                value = changes_0['value']
                message = value['messages'][0]

                data_schema = {
                    'message_id': message['id'],
                    'message_from': message['from'],
                    'message_timestamp': message['timestamp'],
                    'message_text': message['text']['body'],
                    'message_type': message['type']
                }

                session = get_session(message_from, message_body, data_schema)
                handle_session(session, phone_number_id)

            return {}, 200
        except Exception as e:
            current_app.logger.error(e, exc_info=True)
            abort(500, description="Something went wrong when processing your request. Please try again later.")
