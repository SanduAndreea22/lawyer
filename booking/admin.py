from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        "client_name",
        "client_phone",
        "practice_area",
        "lawyer",
        "start_time",
        "status",
    ]
    list_filter = ["status", "practice_area", "lawyer"]
    list_editable = ["status"]
    search_fields = ["client_name", "client_phone"]
    date_hierarchy = "start_time"
