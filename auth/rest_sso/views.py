# coding: utf-8
from __future__ import absolute_import, unicode_literals

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import claims
from .models import SessionToken
from .serializers import SessionTokenSerializer, AuthorizationTokenSerializer
from .settings import api_settings

import logging

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


obtain_session_token = ObtainSessionTokenView.as_view()
obtain_authorization_token = ObtainAuthorizationTokenView.as_view()
