INSTALLED_APPS = [
    "rssfilter",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

ROOT_URLCONF = "rssfilter.urls"

SECRET_KEY = "test_secret_key"
