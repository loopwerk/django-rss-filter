from dataclasses import dataclass
from typing import Literal

import feedparser
import httpx
from feedgen.feed import FeedGenerator
from feedparser import FeedParserDict
from httpx import ConnectError, ConnectTimeout

from . import USER_AGENT


@dataclass
class FeedValidationSuccess:
    valid: Literal[True]
    feed: FeedParserDict


@dataclass
class FeedValidationError:
    valid: Literal[False]
    error: str


def validate_feed(feed_url: str) -> FeedValidationSuccess | FeedValidationError:
    try:
        # Fetch content using httpx rather than having feedparser do this,
        # since we can't set a timeout with feedparser. It also makes sure
        # that validating and then fetching the feed is done in a consistent
        # manner.
        r = httpx.get(feed_url, follow_redirects=True, timeout=2, headers={"User-Agent": USER_AGENT})
        feed = validate_feed_body(r.text)
        if not feed:
            return FeedValidationError(False, "This doesn't seem to be a valid RSS or Atom feed")
        return FeedValidationSuccess(True, feed)
    except ConnectTimeout:
        return FeedValidationError(False, "Couldn't load the URL due to a connection timeout")
    except ConnectError:
        return FeedValidationError(False, "Couldn't load the URL due to a connection error")


def validate_feed_body(body: str) -> Literal[False] | FeedParserDict:
    try:
        feed = feedparser.parse(body)
        return feed if feed.version else False
    except AttributeError:
        return False
    except ValueError:
        return False


def filter_feed(feed_body: str, filtered_words: str, filtered_categories: str) -> str:
    feed = feedparser.parse(feed_body)

    fg = FeedGenerator()
    fg.id(feed.feed.get("id", feed.feed.link))
    fg.title(feed.feed.title)
    fg.link(href=feed.feed.link)
    fg.description(feed.feed.get("description", "Filtered feed"))
    fg.language(feed.feed.get("language", "en"))

    if updated := feed.feed.get("updated"):
        fg.updated(updated)

    if published := feed.feed.get("published"):
        fg.pubDate(published)

    filtered_words_list = [item.lower().strip().strip('"').strip("'") for item in filtered_words.split(",")]
    filtered_categories_list = [item.lower().strip().strip('"').strip("'") for item in filtered_categories.split(",")]

    # Filter out empty strings
    filtered_words_list = [x for x in filtered_words_list if x]
    filtered_categories_list = [x for x in filtered_categories_list if x]

    for entry in feed.entries:
        # Check if the title contains filtered words
        if len(filtered_words_list):
            if any(word in entry.title.lower() for word in filtered_words_list):
                continue

        # Check if the categories/terms contain filtered categories
        if len(filtered_categories_list) and hasattr(entry, "tags"):
            terms = [tag.term.lower() for tag in entry.tags]
            if any(filtered_category in term for term in terms for filtered_category in filtered_categories_list):
                continue

        fe = fg.add_entry()
        fe.id(entry.get("id", entry.link))
        fe.title(entry.title)
        fe.link(href=entry.link)
        fe.description(entry.get("description", ""))
        fe.pubDate(entry.get("published", None))

    return fg.atom_str(pretty=True).decode("utf-8")
