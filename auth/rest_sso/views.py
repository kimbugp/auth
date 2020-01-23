# coding: utf-8
from __future__ import absolute_import, unicode_literals

import json
import logging
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import claims
from .models import SessionToken
from .serializers import (
    AuthorizationTokenSerializer,
    SessionTokenSerializer,
    UserSerializer,
)
from .settings import api_settings

logger = logging.getLogger(__name__)

create_session_payload = api_settings.CREATE_SESSION_PAYLOAD
create_authorization_payload = api_settings.CREATE_AUTHORIZATION_PAYLOAD
encode_jwt_token = api_settings.ENCODE_JWT_TOKEN
decode_jwt_token = api_settings.DECODE_JWT_TOKEN


class BaseAPIView(APIView):
    throttle_classes = ()
    permission_classes = ()
    serializer_class = None

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {"request": self.request, "view": self}

    def get_serializer_class(self):
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method." % self.__class__.__name__
        )
        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class ObtainSessionTokenView(BaseAPIView):
    permission_classes = ()
    serializer_class = SessionTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        session_token = (
            SessionToken.objects.active()
            .filter(user=user)
            .with_user_agent(request=request)
            .first()
        )
        if session_token is None:
            session_token = SessionToken(user=user)
        session_token.update_attributes(request=request)
        session_token.save()
        payload = create_session_payload(session_token=session_token, user=user)
        jwt_token = encode_jwt_token(payload=payload)
        return Response({"token": jwt_token})


class ObtainAuthorizationTokenView(BaseAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AuthorizationTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if hasattr(request.auth, "get") and request.auth.get(claims.SESSION_ID):
            try:
                session_token = SessionToken.objects.active().get(
                    pk=request.auth.get(claims.SESSION_ID), user=request.user
                )
            except SessionToken.DoesNotExist:
                return Response(
                    {"detail": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            session_token = (
                SessionToken.objects.active()
                .filter(user=request.user)
                .with_user_agent(request=request)
                .first()
            )
            if session_token is None:
                session_token = SessionToken(user=request.user)

        session_token.update_attributes(request=request)
        session_token.save()
        payload = create_authorization_payload(
            session_token=session_token, user=request.user, **serializer.validated_data
        )
        jwt_token = encode_jwt_token(payload=payload)
        return Response({"token": jwt_token})


class CreateUserView(CreateAPIView):

    model = get_user_model()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer


def public_key(request):
    file_path = os.path.join(settings.KEYS_PATH, "keys.json")
    if os.path.exists(file_path):
        with open(file_path, "rb") as fh:
            response = HttpResponse(fh.read(), content_type="application/json")
            return response
    return HttpResponse(
        json.dumps({"error": "file not found"}), content_type="application/json"
    )


class SingleUserView(RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    lookup_field = "id"
    permission_classes = [AllowAny]


obtain_session_token = ObtainSessionTokenView.as_view()
obtain_authorization_token = ObtainAuthorizationTokenView.as_view()
create_user = CreateUserView.as_view()
view_user = SingleUserView.as_view()
