# coding: utf-8
import logging
import os
import textwrap

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (load_pem_private_key,
                                                          load_pem_public_key)
from cryptography.x509 import load_pem_x509_certificate
from django.utils import six
from jwt.exceptions import InvalidKeyError
from django.conf import settings
from .settings import api_settings

logger = logging.getLogger(__name__)


def get_file(file_name):
    file_path = os.path.join(settings.KEYS_PATH, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            return fh.read()


def get_private_key_and_key_id(issuer, key_id=None, file_name='key.pem'):
    file_data = get_file(file_name=file_name)
    key = load_pem_private_key(
        file_data, password=b'stylist', backend=default_backend())
    return key, key_id


def get_public_key_and_key_id(issuer, key_id=None):
    public_key = get_file(file_name='pubkey.pem')
    certificate = load_pem_public_key(public_key, backend=default_backend())
    return certificate, key_id
