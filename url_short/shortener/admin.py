from django.contrib import admin

from .models import Link


class LinkAdmin(admin.ModelAdmin):
    list_display = ('short_code', 'original_link', 'created_at')
    search_fields = ('short_code', 'original_link')

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Link, LinkAdmin)
