from __future__ import absolute_import

import datetime
import uuid
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now)
    last_modified = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now)


class MarshmallowSchema(SQLAlchemyAutoSchema):
    date_created = fields.DateTime(format='%Y-%m-%d %H:%M')
    last_modified = fields.DateTime(format='%Y-%m-%d %H:%M')
