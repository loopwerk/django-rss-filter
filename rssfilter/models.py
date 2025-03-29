import uuid
from datetime import timedelta

import httpx
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from .settings import RSS_FILTER_CACHE_SECONDS
from .utils import filter_feed, validate_feed


class FilteredFeed(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)
    feed_url = models.URLField()
    filtered_words = models.CharField(max_length=1024, blank=True)
    filtered_categories = models.CharField(max_length=1024, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    cache_date = models.DateTimeField(null=True, editable=False)
    filtered_feed_body = models.TextField(editable=False)

    def __str__(self):
        return f"Feed {self.uuid}"

    def clean(self):
        super().clean()

        # Make sure we have a valid feed.
        # Let's assume it's valid if it's already in FeedCache.
        if not FeedCache.objects.filter(feed_url=self.feed_url).exists():
            if not validate_feed(self.feed_url):
                raise ValidationError({"feed_url": "This doesn't seem to be a valid RSS or Atom feed"})

    def get_filtered_feed_body(self) -> str:
        five_mins_ago = timezone.now() - timedelta(seconds=RSS_FILTER_CACHE_SECONDS)
        if self.cache_date and self.cache_date > five_mins_ago:
            return self.filtered_feed_body

        feed_cache, _created = FeedCache.objects.get_or_create(feed_url=self.feed_url)

        self.filtered_feed_body = filter_feed(feed_cache.get_feed_body(), self.filtered_words, self.filtered_categories)
        self.cache_date = timezone.now()
        self.save()

        return self.filtered_feed_body

    def get_absolute_url(self):
        return reverse("rss-filter-feed", args=[self.uuid])


class FeedCache(models.Model):
    feed_url = models.URLField(unique=True, db_index=True)
    cache_date = models.DateTimeField(null=True)
    feed_body = models.TextField()

    def get_feed_body(self) -> str:
        five_mins_ago = timezone.now() - timedelta(seconds=RSS_FILTER_CACHE_SECONDS)
        if self.cache_date and self.cache_date > five_mins_ago:
            return self.feed_body

        r = httpx.get(self.feed_url)
        self.feed_body = r.text
        self.cache_date = timezone.now()
        self.save()

        return self.feed_body
