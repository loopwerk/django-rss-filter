# django-rss-filter

This is a Django app that creates filtered RSS feeds. It does this by filtering existing RSS feeds, removing articles that match filtered words and/or filtered categories. It's what powers https://www.rssfilter.com.

It comes with one view that returns the filtered feed XML, as well as Django Admin configuration to make it possible and easy to self-host your own instance of django-rss-filter. It does not come with views to create or edit filtered feeds; this can be done using the Django Admin.

## Getting started

All instructions use [uv](https://docs.astral.sh/uv/), but should work just as well with pip or Poetry for example.

In an existing Django project:

1. Install: `uv add django-rss-filter`
2. Add `rssfilter` to `INSTALLED_APPS`
3. `uv run ./manage.py migrate`
4. Include the URL config: `path("", include("rssfilter.urls"))`

If you don't have a Django project yet, these are the steps to get started:

1. `uv init my-django-project`
2. `cd my-django-project`
3. `uv add django`
4. `uv run django-admin startproject my_django_app .`
5. `uv run ./manage.py migrate`
6. `uv run ./manage.py createsuperuser`
7. `uv run ./manage.py runserver`

This will get you up and running with a working Admin site at http://127.0.0.1:8000/admin/.

Then follow the first four steps to add django-rss-filter to your Django project.

## Example project

There's an example Django project using django-rss-filter under `example/`.

1. `cd example`
2. `uv run ./manage.py migrate`
3. `uv run ./manage.py createsuperuser`
4. `uv run ./manage.py runserver`

You can then go to http://127.0.0.1:8000/admin/ to create a feed, which you can then access at http://127.0.0.1:8000/[feed_uuid]/.

## Settings

There is one setting that can be configured: `RSS_FILTER_CACHE_SECONDS`. The default value is 300 (5 minutes).

This setting controls how long a feed will be cached before it's fetched, filtered, and stored again.

## Tests

Unit tests can be run with `uv run pytest`.

## About Feature Requests

This project is feature-complete — it does what I needed it to do, and I’m not actively looking to expand its functionality.

I’m not accepting feature requests via issues. Please understand that asking for new features is essentially asking for free work — not just to build something, but to maintain it over time. And since I don’t personally need those features, I’m unlikely to invest time in them.

If you’d like to add a new feature, you’re welcome to open a pull request. Just know that I’ll evaluate it carefully, because even merged contributions become part of what I maintain. To avoid spending time on a PR that may not be accepted, I recommend starting a discussion first — that way we can talk through the idea and see if it fits.

This approach helps me avoid burnout and keep the project sustainable. Thanks for understanding!
