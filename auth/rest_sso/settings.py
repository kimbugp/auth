# coding: utf-8
from __future__ import absolute_import, unicode_literals

import datetime

from django.conf import settings
from django.test.signals import setting_changed
from rest_framework.settings import APISettings


USER_SETTINGS = getattr(settings, "REST_SSO", None)

DEFAULTS = {
    "CREATE_SESSION_PAYLOAD": "auth.rest_sso.utils.create_session_payload",
    "CREATE_AUTHORIZATION_PAYLOAD": "auth.rest_sso.utils.create_authorization_payload",
    "ENCODE_JWT_TOKEN": "auth.rest_sso.utils.encode_jwt_token",
    "DECODE_JWT_TOKEN": "auth.rest_sso.utils.decode_jwt_token",
    "AUTHENTICATE_PAYLOAD": "auth.rest_sso.utils.authenticate_payload",
    "ENCODE_ALGORITHM": "RS256",
    "DECODE_ALGORITHMS": None,
    "VERIFY_SIGNATURE": True,
    "VERIFY_EXPIRATION": True,
    "VERIFY_ISSUER": True,
    "VERIFY_AUDIENCE": True,
    "VERIFY_SESSION_TOKEN": True,
    "EXPIRATION_LEEWAY": 0,
    "SESSION_EXPIRATION": None,
    "AUTHORIZATION_EXPIRATION": datetime.timedelta(seconds=300),
    "IDENTITY": None,
    "SESSION_AUDIENCE": None,
    "AUTHORIZATION_AUDIENCE": None,
    "ACCEPTED_ISSUERS": None,
    "KEY_STORE_ROOT": None,
    "PUBLIC_KEYS": {},
    "PRIVATE_KEYS": {},
    "AUTHENTICATE_HEADER": "Bearer",
}

# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    "CREATE_SESSION_PAYLOAD",
    "CREATE_AUTHORIZATION_PAYLOAD",
    "ENCODE_JWT_TOKEN",
    "DECODE_JWT_TOKEN",
    "AUTHENTICATE_PAYLOAD",
)

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*args, **kwargs):
    global api_settings
    setting, value = kwargs["setting"], kwargs["value"]
    if setting == "REST_SSO":
        api_settings = APISettings(value, DEFAULTS, IMPORT_STRINGS)


setting_changed.connect(reload_api_settings)
