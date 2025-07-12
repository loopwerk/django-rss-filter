import uuid
from datetime import timedelta

import httpx
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from httpx import ConnectError, ConnectTimeout, ReadTimeout

from . import USER_AGENT
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
            result = validate_feed(self.feed_url)
            if not result.valid:
                raise ValidationError({"feed_url": result.error})

    def save(self, *args, **kwargs):
        if self.pk:
            old = FilteredFeed.objects.get(pk=self.pk)
            if (
                old.feed_url != self.feed_url
                or old.filtered_words != self.filtered_words
                or old.filtered_categories != self.filtered_categories
            ):
                self.cache_date = None
                self.filtered_feed_body = ""

        super().save(*args, **kwargs)

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

        try:
            r = httpx.get(self.feed_url, follow_redirects=True, timeout=2, headers={"User-Agent": USER_AGENT})
            self.feed_body = r.text
            self.cache_date = timezone.now()
            self.save()
        except (ConnectTimeout, ConnectError, ReadTimeout):
            # Do nothing, just return the cached version (if available)
            pass

        return self.feed_body
