# coding: utf-8
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
)
from django.utils import six
from jwt.exceptions import InvalidKeyError

from .settings import api_settings

import logging

logger = logging.getLogger(__name__)


def get_private_key_and_key_id(issuer, key_id=None):
    return api_settings.PRIVATE_KEYS.get(issuer), key_id
