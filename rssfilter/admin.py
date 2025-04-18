from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import FilteredFeed


@admin.register(FilteredFeed)
class FilteredFeedAdmin(admin.ModelAdmin):
    list_display = ["id", "created", "feed_url", "filtered_words", "filtered_categories", "view"]
    search_fields = ["uuid", "feed_url"]
    date_hierarchy = "created"
    ordering = ["-id"]

    def view(self, obj):
        return mark_safe(f'<a href="{obj.get_absolute_url()}">Open</a>')

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs["exclude"] = ["uuid"]
        return super().get_form(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["uuid"]
        return self.readonly_fields
