from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "created_at", "is_read"]
    list_editable = ["is_read"]
    search_fields = ["name", "phone"]
