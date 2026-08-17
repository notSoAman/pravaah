"""
URL configuration for PRAVAAH.
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from pravaah.views import (
    home,
    events_list,
    event_detail,
    team_list,
    films_list,
    journal_list,
    journal_detail,
    health_check,
)

from django.urls import re_path
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health_check"),
    path("", home, name="home"),
    path("events/", events_list, name="events_list"),
    path("events/<slug:slug>/", event_detail, name="event_detail"),
    path("team/", team_list, name="team"),
    path("films/", films_list, name="films_list"),
    path("journal/", journal_list, name="journal_list"),
    path("journal/<slug:slug>/", journal_detail, name="journal_detail"),
]

# Serve uploaded media files (in both dev and production when R2 is disabled)
if not getattr(settings, "USE_R2", False):
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

