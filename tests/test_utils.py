import feedparser
from django.test import TestCase

from rssfilter.utils import filter_feed, validate_feed_body

body = """
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:thr="http://purl.org/syndication/thread/1.0" xml:lang="en-US">
	<title type="text">Example Feeed</title>
	<updated>2025-03-28T18:18:49+00:00</updated>
	<id>https://www.example.com/rss/index.xml</id>
    <link>https://www.example.com</link>
	<entry>
		<title>Article One</title>
		<link>https://www.example.com/one/</link>
		<updated>2025-03-28T14:18:49-04:00</updated>
		<published>2025-03-28T14:18:49-04:00</published>
		<category term="Category One" />
		<category term="Category Two" />
		<summary>Article Summary</summary>
		<content>Article Content</content>
	</entry>
    <entry>
		<title>Article Two</title>
		<link>https://www.example.com/two/</link>
		<updated>2025-03-28T14:18:49-04:00</updated>
		<published>2025-03-28T14:18:49-04:00</published>
		<category term="Category Three" />
		<category term="Category Four" />
		<summary>Article Summary</summary>
		<content>Article Content</content>
	</entry>
</feed>
"""


class UtilsTest(TestCase):
    def test_validate_feed_body_vlaid(self):
        result = validate_feed_body(body)
        self.assertTrue(result)

    def test_validate_feed_body_invalid(self):
        result = validate_feed_body("<html>Hello</html>")
        self.assertFalse(result)

    def test_validate_feed_body_empty(self):
        result = validate_feed_body("")
        self.assertFalse(result)

    def test_filter_words(self):
        filtered_feed_body = filter_feed(body, filtered_words="One", filtered_categories="")
        filtered_feed = feedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 1)
        self.assertEqual(filtered_feed.entries[0].title, "Article Two")

    def test_filter_words_case_insenstive(self):
        filtered_feed_body = filter_feed(body, filtered_words="ONE", filtered_categories="")
        filtered_feed = feedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 1)
        self.assertEqual(filtered_feed.entries[0].title, "Article Two")

    def test_filter_words_empty(self):
        filtered_feed_body = filter_feed(body, filtered_words="", filtered_categories="")
        filtered_feed = feedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 2)

    def test_filter_words_with_empty_quotes(self):
        filtered_feed_body = filter_feed(body, filtered_words='""', filtered_categories="")
        filtered_feed = feedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 2)

    def test_filter_words_not_found(self):
        filtered_feed_body = filter_feed(body, filtered_words="Foo", filtered_categories="")
        filtered_feed = feedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 2)

    def test_filter_words_comma_seperated(self):
        filtered_feed_body = filter_feed(body, filtered_words="Foo, Bar, One", filtered_categories="")
        filtered_feed = feedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 1)
        self.assertEqual(filtered_feed.entries[0].title, "Article Two")

    def test_filter_words_with_quotes(self):
        filtered_feed_body = filter_feed(body, filtered_words="'Foo', 'Bar', 'One'", filtered_categories="")
        filtered_feed = feedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 1)
        self.assertEqual(filtered_feed.entries[0].title, "Article Two")

    def test_filter_words_with_double_quotes(self):
        filtered_feed_body = filter_feed(body, filtered_words='"Foo", "Bar", "One"', filtered_categories="")
        filtered_feed = feedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 1)
        self.assertEqual(filtered_feed.entries[0].title, "Article Two")

    def test_filter_categories(self):
        filtered_feed_body = filter_feed(body, filtered_words="", filtered_categories="Category Four")
        filtered_feed = feedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 1)
        self.assertEqual(filtered_feed.entries[0].title, "Article One")
