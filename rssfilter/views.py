from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import FilteredFeed


def feed_view(request, feed_uuid):
    feed = get_object_or_404(FilteredFeed, uuid=feed_uuid)
    return HttpResponse(feed.get_filtered_feed_body(), content_type="application/xml")
