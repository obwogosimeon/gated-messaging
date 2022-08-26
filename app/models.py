from __future__ import absolute_import

from . import db, BaseModel, MarshmallowSchema


class WhatsAppSession(BaseModel):
    __tablename__ = "whatsapp_session"
    phone_number = db.Column(db.String)
    next_screen = db.Column(db.String)
    session_data = db.Column(db.String)


class WhatsAppMessage(BaseModel):
    __tablename__ = "whatsapp_message"
    message_id = db.Column(db.String)
    message_from = db.Column(db.String)
    message_timestamp = db.Column(db.String)
    message_text = db.Column(db.String)
    message_type = db.Column(db.String)


class EmailMessage(BaseModel):
    __tablename__ = "email_message"
    email_address = db.Column(db.String)
    subject = db.Column(db.String)
    body = db.Column(db.String)
    sent = db.Column(db.Boolean)
    send_at = db.Column(db.DateTime)


class EmailMessageSchema(MarshmallowSchema):
    class Meta:
        model = EmailMessage
        include_fk = True


class SMS(BaseModel):
    __tablename__ = "sms"
    phone = db.Column(db.String)
    message = db.Column(db.String)
    sent = db.Column(db.Boolean, default=False)
    send_at = db.Column(db.DateTime)


class SMSSchema(MarshmallowSchema):
    class Meta:
        model = SMS
        include_fk = True
