from django.conf import settings

RSS_FILTER_CACHE_SECONDS = getattr(settings, "RSS_FILTER_CACHE_SECONDS", 5 * 60)
