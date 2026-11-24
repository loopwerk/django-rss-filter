from xml.etree import ElementTree

import fastfeedparser
from django.test import TestCase

from rssfilter.utils import filter_feed, validate_feed_body

body = """
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:thr="http://purl.org/syndication/thread/1.0" xml:lang="en-US">
	<title type="text">Example Feeed</title>
	<updated>2025-03-28T18:18:49+00:00</updated>
	<id>https://www.example.com/rss/index.xml</id>
    <link href="https://www.example.com" />
	<entry>
		<title>Article One</title>
		<link href="https://www.example.com/one/" />
		<updated>2025-03-28T14:18:49-04:00</updated>
		<published>2025-03-28T14:18:49-04:00</published>
		<category term="Category One" />
		<category term="Category Two" />
		<summary>Article Summary</summary>
		<content>Article Content</content>
	</entry>
    <entry>
		<title>Article Two</title>
		<link href="https://www.example.com/two/" />
		<updated>2025-03-28T14:18:49-04:00</updated>
		<published>2025-03-28T14:18:49-04:00</published>
		<category term="Category Three" />
		<category term="Category Four" />
		<summary>Article Summary</summary>
		<content>Article Content</content>
	</entry>
</feed>
"""


ATOM_ID = "{http://www.w3.org/2005/Atom}id"
ATOM_LINK = "{http://www.w3.org/2005/Atom}link"


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
        filtered_feed = fastfeedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 1)
        self.assertEqual(filtered_feed.entries[0].title, "Article Two")

    def test_filter_words_case_insenstive(self):
        filtered_feed_body = filter_feed(body, filtered_words="ONE", filtered_categories="")
        filtered_feed = fastfeedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 1)
        self.assertEqual(filtered_feed.entries[0].title, "Article Two")

    def test_filter_words_empty(self):
        filtered_feed_body = filter_feed(body, filtered_words="", filtered_categories="")
        filtered_feed = fastfeedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 2)

    def test_filter_words_with_empty_quotes(self):
        filtered_feed_body = filter_feed(body, filtered_words='""', filtered_categories="")
        filtered_feed = fastfeedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 2)

    def test_filter_words_not_found(self):
        filtered_feed_body = filter_feed(body, filtered_words="Foo", filtered_categories="")
        filtered_feed = fastfeedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 2)

    def test_filter_words_comma_seperated(self):
        filtered_feed_body = filter_feed(body, filtered_words="Foo, Bar, One", filtered_categories="")
        filtered_feed = fastfeedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 1)
        self.assertEqual(filtered_feed.entries[0].title, "Article Two")

    def test_filter_words_with_quotes(self):
        filtered_feed_body = filter_feed(body, filtered_words="'Foo', 'Bar', 'One'", filtered_categories="")
        filtered_feed = fastfeedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 1)
        self.assertEqual(filtered_feed.entries[0].title, "Article Two")

    def test_filter_words_with_double_quotes(self):
        filtered_feed_body = filter_feed(body, filtered_words='"Foo", "Bar", "One"', filtered_categories="")
        filtered_feed = fastfeedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 1)
        self.assertEqual(filtered_feed.entries[0].title, "Article Two")

    def test_entry_without_link(self):
        body_without_links = """
        <?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <title type="text">Example Feed</title>
            <updated>2025-03-28T18:18:49+00:00</updated>
            <id>https://www.example.com/rss/index.xml</id>
            <entry>
                <title>Article One</title>
                <id>https://www.example.com/one/</id>
                <updated>2025-03-28T14:18:49-04:00</updated>
                <summary>Article Summary</summary>
            </entry>
        </feed>
        """
        filtered_feed_body = filter_feed(body_without_links, filtered_words="", filtered_categories="")
        filtered_feed = fastfeedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 1)
        self.assertEqual(filtered_feed.entries[0].title, "Article One")

    def test_filter_categories(self):
        filtered_feed_body = filter_feed(body, filtered_words="", filtered_categories="Category Four")
        filtered_feed = fastfeedparser.parse(filtered_feed_body)

        self.assertEqual(len(filtered_feed.entries), 1)
        self.assertEqual(filtered_feed.entries[0].title, "Article One")

    def test_feed_identifies_itself(self):
        filtered_feed_body = filter_feed(
            body,
            filtered_words="",
            filtered_categories="",
            feed_id="urn:uuid:ca0447ad-58e4-4fee-be44-1743c506415d",
            self_url="https://www.rssfilter.com/ca0447ad-58e4-4fee-be44-1743c506415d/",
        )
        feed = ElementTree.fromstring(filtered_feed_body)
        links = {link.get("rel"): link.get("href") for link in feed.findall(ATOM_LINK)}

        # Neither the id nor the "self" link may point at the original feed,
        # or feed readers will subscribe to that one instead.
        self.assertEqual(feed.findtext(ATOM_ID), "urn:uuid:ca0447ad-58e4-4fee-be44-1743c506415d")
        self.assertEqual(links["self"], "https://www.rssfilter.com/ca0447ad-58e4-4fee-be44-1743c506415d/")

        # The original website is still linked, but only as the alternate.
        self.assertEqual(links["alternate"], "https://www.example.com")

    def test_feed_id_falls_back_to_self_url(self):
        filtered_feed_body = filter_feed(
            body,
            filtered_words="",
            filtered_categories="",
            self_url="https://www.rssfilter.com/ca0447ad-58e4-4fee-be44-1743c506415d/",
        )
        feed = ElementTree.fromstring(filtered_feed_body)

        self.assertEqual(feed.findtext(ATOM_ID), "https://www.rssfilter.com/ca0447ad-58e4-4fee-be44-1743c506415d/")

    def test_feed_without_self_url(self):
        filtered_feed_body = filter_feed(body, filtered_words="", filtered_categories="")
        feed = ElementTree.fromstring(filtered_feed_body)
        links = {link.get("rel"): link.get("href") for link in feed.findall(ATOM_LINK)}

        self.assertEqual(feed.findtext(ATOM_ID), "https://www.example.com/rss/index.xml")
        self.assertNotIn("self", links)
        self.assertEqual(links["alternate"], "https://www.example.com")

    def test_entries_keep_their_original_links(self):
        filtered_feed_body = filter_feed(
            body,
            filtered_words="",
            filtered_categories="",
            self_url="https://www.rssfilter.com/ca0447ad-58e4-4fee-be44-1743c506415d/",
        )
        filtered_feed = fastfeedparser.parse(filtered_feed_body)

        self.assertEqual(
            sorted(entry.link for entry in filtered_feed.entries),
            ["https://www.example.com/one/", "https://www.example.com/two/"],
        )
