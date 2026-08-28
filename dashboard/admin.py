from django.contrib import admin

from .models import Case, Document, Invoice


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0


class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 0


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ["client_name", "lawyer", "practice_area", "status", "updated_at"]
    list_filter = ["status", "practice_area", "lawyer"]
    list_editable = ["status"]
    search_fields = ["client_name", "client_phone"]
    inlines = [DocumentInline, InvoiceInline]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["case", "label", "uploaded_at"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["case", "amount", "status", "due_date"]
    list_filter = ["status"]
    list_editable = ["status"]
