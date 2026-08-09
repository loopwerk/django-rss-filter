# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`django-rss-filter` is a reusable Django **app** (not a standalone project) published to PyPI as `django-rss-filter`. It serves filtered versions of public RSS/Atom feeds, dropping entries whose title contains filtered words or whose categories match filtered categories. It powers https://www.rssfilter.com.

The app deliberately ships only a read view plus Django Admin config — there are no create/edit views. Feeds are managed through the Admin.

## Commands

Run from the repo root (a `justfile` wraps these):

- `just test` / `uv run pytest` — run the test suite (pytest-django, settings from `tests/settings.py`, in-memory SQLite)
- `uv run pytest tests/test_utils.py::UtilsTest::test_filter_words` — run a single test
- `just check` / `uv run ruff check . && uv run mypy .` — lint + type check (both run in CI)
- `just format` / `uv run ruff format .` — format (line length 120, isort + pep8-naming rules enabled)

Example project (`example/`, installs the parent as an editable path dependency):

- `cd example && just run` — `manage.py runserver`; Admin at http://127.0.0.1:8000/admin/, feed at `http://127.0.0.1:8000/<feed_uuid>`

## Architecture

Two models in `rssfilter/models.py` implement a **two-level cache**, which is the core design idea:

- `FeedCache` — one row per upstream `feed_url`, holding the raw fetched body. Shared across all `FilteredFeed`s pointing at the same URL, so N users filtering the same feed cause one upstream fetch per cache window. On network failure (`ConnectTimeout`/`ConnectError`/`ReadTimeout`) it silently returns the stale body rather than erroring.
- `FilteredFeed` — one row per user-created filter, holding the *rendered* filtered output in `filtered_feed_body`. `save()` invalidates this cache (`cache_date = None`, body cleared) whenever `feed_url`, `filtered_words`, or `filtered_categories` change.

Both levels use the same TTL: `RSS_FILTER_CACHE_SECONDS` (default 300s), read via `rssfilter/settings.py`, which is the standard `getattr(settings, ...)` shim for app-level settings.

Request flow: `urls.py` (`<uuid:feed_uuid>` → `rss-filter-feed`) → `views.py:feed_view` → `FilteredFeed.get_filtered_feed_body()` → `FeedCache.get_feed_body()` → `utils.filter_feed()`. Feeds are addressed by a random `uuid` field, not by pk — the pk is never exposed.

`rssfilter/utils.py`:
- `validate_feed(url)` / `validate_feed_body(body)` — used by `FilteredFeed.clean()` so the Admin rejects non-feed URLs. Returns a `FeedValidationSuccess | FeedValidationError` dataclass union rather than raising. Validation is skipped when a `FeedCache` row already exists for the URL.
- `filter_feed(body, words, categories)` — parses with `fastfeedparser`, re-emits with `feedgen`. **Output is always Atom** (`fg.atom_str()`) regardless of the input format. Filter terms are comma-separated, lowercased, and stripped of surrounding quotes; matching is substring-based (words against `entry.title`, categories against `entry.tags[].term`).

  Two `fastfeedparser` quirks shape this code: absent values come back as `None` rather than being omitted (so `or` is used for fallbacks, not `get`'s default), and an RSS `<description>` surfaces as `subtitle`. It resolves an entry's `id` from `<id>`/`<guid>`/RDF `about`, falling back to the link; entries with neither are skipped, since Atom requires an id. Note it reads Atom links **only** from the `href` attribute, so `<link>https://…</link>` (invalid Atom, but accepted by some parsers) yields no link.

HTTP is done with `httpx2` (not `httpx`) everywhere, always with `follow_redirects=True`, `timeout=2`, and the `USER_AGENT` from `rssfilter/__init__.py`. Fetching is intentionally done via httpx rather than letting the parser fetch, so a timeout can be set and validation/fetching behave consistently. Downstream apps are expected to override `rssfilter.USER_AGENT` at import time.

## Conventions

- Dependencies are managed with `uv`; keep `uv.lock` in sync and don't hand-edit it.
- Supported matrix is broad — Python ≥3.10 and Django ≥4.2 — so avoid newer-only syntax/APIs. CI tests 3.10–3.13.
- Migrations live in `rssfilter/migrations/` and are excluded from mypy. Model changes need a migration checked in.
- Releases: push a git tag matching `project.version` in `pyproject.toml` exactly; the release workflow validates the match, then lints, tests, builds, publishes to PyPI, and generates a changelog. Commit messages feed that changelog — `feat:`/`fix:` appear, `other`/`doc`/`chore`/`build` are excluded.

## Code comments

Keep comments short and about the code _as it is now_. A comment must explain what the current code does or why, for someone reading it fresh.

- **If the code is obvious, don't comment it.** A comment that just restates what the code plainly says is noise. Only add one when it earns its place.
- **Plain language a junior can follow.** Describe the situation in everyday terms; avoid framework-internals jargon (e.g. "app population", "reverse-relation tree", "OneToOneRel").
- **Never narrate history.** Don't describe what the code used to do, what a previous attempt was, what changed, or why the old approach was abandoned. Git already records this. Such notes are stale the moment they're written and add noise.
- **No changelogs, dates, names, or PR/review references in code.** That context belongs in the commit message or PR description.
- **Prefer one or two plain sentences** over multi-line paragraphs. If a comment needs a paragraph to justify the code, the code usually needs the rework, not the essay.
- Comment the non-obvious _why_ (a workaround for a specific client bug, an ordering constraint), not the obvious _what_.

## Code style

- **Imports go at the top of the file.** Never put imports inside functions or fixtures to dodge ordering/lint warnings. The only acceptable inline import is to break a genuine circular import.
- **Never put a real e-mail address (or other real user PII) in code, comments, or tests.** Real user data must not leak into our code. Use the reserved example domains for placeholders — `john@example.com`, `name@example.org`.