from django.urls import path

from .views import feed_view

urlpatterns = [
    path("<uuid:feed_uuid>", feed_view, name="rss-filter-feed"),
]
