from __future__ import absolute_import

import dateutil.parser
from flask import current_app, request
from flask_restful import Resource, reqparse, abort

from .. import db
from ..models import SMS, SMSSchema
from ..utils import verify_basic_auth, sanitise_phone_number


class SMSResource(Resource):
    def __init__(self):
        super(self.__class__, self).__init__()

    def get(self):
        # authorization
        auth_username = request.authorization["username"] if request.authorization else False
        auth_password = request.authorization["password"] if request.authorization else False

        if not verify_basic_auth(auth_username, auth_password):
            abort(400, description="Access denied")

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('phone', required=False, help='phone number')

        args = parser.parse_args()

        if args['phone']:
            return SMSSchema().dump(SMS.query.filter_by(phone=sanitise_phone_number(args['phone'])).order_by(
                SMS.date_created.desc()
            ).all())

        return SMSSchema(many=True).dump(SMS.query.order_by(SMS.date_created.desc()).all())

    def post(self):
        # authorization
        auth_username = request.authorization["username"] if request.authorization else False
        auth_password = request.authorization["password"] if request.authorization else False

        if not verify_basic_auth(auth_username, auth_password):
            abort(400, description="Access denied")

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('phone', required=True, help='phone')
        parser.add_argument('message', required=True, help='message')
        parser.add_argument('send_at', required=True, help='time to send')

        args = parser.parse_args()

        for phone in args['phone'].split(","):
            kwargs = {
                'phone': sanitise_phone_number(phone),
                'message': args['message'],
                'send_at': dateutil.parser.parse(args['send_at']),
                'sent': False
            }

            try:
                new_message = SMS(**kwargs)
                db.session.add(new_message)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(e, exc_info=True)

        return {'success': True, 'message': 'messages queued and will be sent.'}, 201
