from django.contrib import admin

from .models import PracticeArea


@admin.register(PracticeArea)
class PracticeAreaAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order", "is_active"]
    list_editable = ["order", "is_active"]
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ["name"]
