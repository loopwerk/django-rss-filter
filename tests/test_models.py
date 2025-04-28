from django.test import TestCase
from django.utils import timezone

from rssfilter.models import FilteredFeed


class ModelsTest(TestCase):
    def test_clear_cache_on_safe(self):
        feed = FilteredFeed.objects.create(
            feed_url="http://www.example.com/",
            cache_date=timezone.now(),
            filtered_feed_body="CACHED",
        )

        self.assertEqual(feed.filtered_feed_body, "CACHED")

        feed.filtered_words = "Changed value"
        feed.save()

        self.assertEqual(feed.cache_date, None)
        self.assertEqual(feed.filtered_feed_body, "")
