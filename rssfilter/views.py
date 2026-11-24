from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import FilteredFeed


def feed_view(request, feed_uuid):
    feed = get_object_or_404(FilteredFeed, uuid=feed_uuid)

    # Tell the feed reader that this URL is the feed, both in the response
    # headers and through the feed's own "self" link, so that it subscribes to
    # the filtered feed instead of looking up the unfiltered original.
    body = feed.get_filtered_feed_body(self_url=request.build_absolute_uri(request.path))
    return HttpResponse(body, content_type="application/atom+xml; charset=utf-8")
