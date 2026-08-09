from dataclasses import dataclass
from typing import Literal

import fastfeedparser
import httpx2
from fastfeedparser import FastFeedParserDict
from feedgen.feed import FeedGenerator
from httpx2 import ConnectError, ConnectTimeout

from . import USER_AGENT


@dataclass
class FeedValidationSuccess:
    valid: Literal[True]
    feed: FastFeedParserDict


@dataclass
class FeedValidationError:
    valid: Literal[False]
    error: str


def validate_feed(feed_url: str) -> FeedValidationSuccess | FeedValidationError:
    try:
        # Fetch content using httpx rather than having fastfeedparser do this,
        # since we can't set a timeout with fastfeedparser. It also makes sure
        # that validating and then fetching the feed is done in a consistent
        # manner.
        r = httpx2.get(feed_url, follow_redirects=True, timeout=2, headers={"User-Agent": USER_AGENT})
        feed = validate_feed_body(r.text)
        if not feed:
            return FeedValidationError(False, "This doesn't seem to be a valid RSS or Atom feed")
        return FeedValidationSuccess(True, feed)
    except ConnectTimeout:
        return FeedValidationError(False, "Couldn't load the URL due to a connection timeout")
    except ConnectError:
        return FeedValidationError(False, "Couldn't load the URL due to a connection error")


def validate_feed_body(body: str) -> Literal[False] | FastFeedParserDict:
    try:
        return fastfeedparser.parse(body)
    except (AttributeError, ValueError):
        return False


def filter_feed(feed_body: str, filtered_words: str, filtered_categories: str) -> str:
    feed = fastfeedparser.parse(feed_body)

    fg = FeedGenerator()
    fg.id(feed.feed.get("id") or feed.feed.get("link"))
    fg.title(feed.feed.title)
    fg.link(href=feed.feed.get("link"))
    fg.description(feed.feed.get("description") or feed.feed.get("subtitle") or "Filtered feed")
    fg.language(feed.feed.get("language") or "en")

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
        if any(word in entry.title.lower() for word in filtered_words_list):
            continue

        # Check if the categories/terms contain filtered categories
        if len(filtered_categories_list) and entry.get("tags"):
            terms = [tag["term"].lower() for tag in entry.tags if tag.get("term")]
            if any(filtered_category in term for term in terms for filtered_category in filtered_categories_list):
                continue

        # An Atom entry is only valid with an id, and the link is the only
        # thing left to fall back on.
        entry_id = entry.get("id") or entry.get("link")
        if not entry_id:
            continue

        fe = fg.add_entry()
        fe.id(entry_id)
        fe.title(entry.title)
        fe.link(href=entry.get("link"))
        fe.description(entry.get("description") or "")
        fe.pubDate(entry.get("published") or None)

    return fg.atom_str(pretty=True).decode("utf-8")
