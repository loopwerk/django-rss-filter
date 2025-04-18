import feedparser
from feedgen.feed import FeedGenerator


def validate_feed(feed_url: str) -> bool:
    try:
        result = feedparser.parse(feed_url)
        if not result.version:
            return False
        return True
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
    fg.updated(feed.feed.updated)

    filtered_words_list = [item.strip().lower() for item in filtered_words.split(",") if item.strip()]
    filtered_categories_list = [item.strip().lower() for item in filtered_categories.split(",") if item.strip()]

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
