from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import path


def health(request):
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
        return JsonResponse({"status": "ok", "database": "up"})
    except Exception:
        return JsonResponse({"status": "error", "database": "down"}, status=503)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
]
