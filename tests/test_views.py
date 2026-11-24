from xml.etree import ElementTree

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rssfilter.models import FeedCache, FilteredFeed

from .test_utils import ATOM_ID, ATOM_LINK, body


class ViewsTest(TestCase):
    def setUp(self):
        self.feed = FilteredFeed.objects.create(feed_url="https://www.example.com/rss/index.xml")

        # Pre-fill the cache so that the view doesn't hit the network.
        FeedCache.objects.create(
            feed_url=self.feed.feed_url,
            cache_date=timezone.now(),
            feed_body=body,
        )

    def test_feed_view_serves_atom(self):
        response = self.client.get(reverse("rss-filter-feed", args=[self.feed.uuid]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/atom+xml; charset=utf-8")

    def test_feed_view_identifies_itself(self):
        url = reverse("rss-filter-feed", args=[self.feed.uuid])
        response = self.client.get(url)

        feed = ElementTree.fromstring(response.content)
        links = {link.get("rel"): link.get("href") for link in feed.findall(ATOM_LINK)}

        self.assertEqual(feed.findtext(ATOM_ID), f"urn:uuid:{self.feed.uuid}")
        self.assertEqual(links["self"], f"http://testserver{url}")
        self.assertEqual(links["alternate"], "https://www.example.com")
