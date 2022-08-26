from __future__ import absolute_import

from flask import Blueprint
from flask_restful import Api

from . import sms_resource

sms = Blueprint('sms', __name__)

api = Api(sms)

api.add_resource(sms_resource.SMSResource, '/sms', endpoint='/sms')
