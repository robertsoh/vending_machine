from django.contrib import admin

from apps.machines.models import Machine


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("machine_id", "name", "is_active", "last_seen_at", "updated_at")
    search_fields = ("machine_id", "name")
    list_filter = ("is_active",)
