from django.urls import include, path

from .views import obtain_authorization_token, obtain_session_token,public_key

urlpatterns = [
    path("session", obtain_session_token),
    path("authorize", obtain_authorization_token),
    path("public", public_key),
]
