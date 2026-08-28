from django.contrib import admin

from .models import Lawyer


@admin.register(Lawyer)
class LawyerAdmin(admin.ModelAdmin):
    list_display = ["name", "specialization", "years_experience", "order", "is_active"]
    list_editable = ["order", "is_active"]
    filter_horizontal = ["practice_areas"]
    search_fields = ["name"]
