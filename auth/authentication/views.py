from rest_framework.decorators import api_view
from django.http import JsonResponse

from .scopes import requires_scope


def public(request):
    return JsonResponse({"message": "Hello from a public endpoint!"})


@api_view(["GET"])
def private(request):
    return JsonResponse({"message": "hello you go it"})


@api_view(["GET"])
@requires_scope("read:messages")
def private_scoped(request):
    return JsonResponse({"message": "you got here"})
