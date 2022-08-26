from __future__ import absolute_import

import phonenumbers
import os


def verify_basic_auth(username, password):
    if (username == os.getenv('AUTH_USER')) and (password == os.getenv('AUTH_PASS')):
        return True

    return False


def sanitise_phone_number(phone):
    try:
        return phonenumbers.format_number(phonenumbers.parse(phone, "KE"), phonenumbers.PhoneNumberFormat.E164)
    except Exception as _:
        return False
