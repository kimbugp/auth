# coding: utf-8
from __future__ import absolute_import, unicode_literals

from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .settings import api_settings

import logging

logger = logging.getLogger(__name__)

create_authorization_payload = api_settings.CREATE_AUTHORIZATION_PAYLOAD
encode_jwt_token = api_settings.ENCODE_JWT_TOKEN


class SessionTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(
        label=_("Password"), style={"input_type": "password"}
    )

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    msg = _("User account is disabled.")
                    raise serializers.ValidationError(msg)
            else:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg)

        attrs["user"] = user
        return attrs


class AuthorizationTokenSerializer(serializers.Serializer):
    pass


UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    is_stylist = serializers.BooleanField(required=False)

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = UserModel.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = UserModel
        fields = (
            "id",
            "username",
            "password",
            "is_stylist",
            "email",
            "first_name",
            "last_name",
        )
