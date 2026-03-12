from django.contrib import admin

from .models import FeatureFlag


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "name_key", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "name_key")
    ordering = ("name_key",)
