from __future__ import absolute_import

from flask import Blueprint
from flask_restful import Api

from . import webhook_resource

whatsapp = Blueprint('whatsapp', __name__)

api = Api(whatsapp)

api.add_resource(webhook_resource.WebhookResource, '/whatsapp/webhook', endpoint='/whatsapp/webhook')
