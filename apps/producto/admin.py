from django.contrib import admin

from apps.producto.models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("machine_id", "slot_no", "product_id", "status", "stock", "price", "updated_at")
    search_fields = ("machine_id", "slot_no", "product_id", "trade_no", "name")
    list_filter = ("machine_id", "status")
