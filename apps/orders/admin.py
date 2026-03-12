from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "machine_id", "slot_number", "product_id", "amount", "status", "created_at")
    list_filter = ("status", "machine_id")
    search_fields = ("id", "machine_id", "product_id", "slot_number")
