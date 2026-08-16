"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
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
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('events/', events_list, name='events_list'),
    path('events/<slug:slug>/', event_detail, name='event_detail'),
    path('team/', team_list, name='team'),
    path('films/', films_list, name='films_list'),
    path('journal/', journal_list, name='journal_list'),
    path('journal/<slug:slug>/', journal_detail, name='journal_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
