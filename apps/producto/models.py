from django.db import models


class Producto(models.Model):
    machine_id = models.CharField(max_length=64, db_index=True)
    slot_no = models.CharField(max_length=32)
    trade_no = models.CharField(max_length=32, db_index=True)
    status = models.PositiveSmallIntegerField()
    quantity = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField()
    product_id = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    s_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_type = models.CharField(max_length=128, blank=True)
    introduction = models.TextField(blank=True)
    modify_type = models.CharField(max_length=32, blank=True)
    lock_goods_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["machine_id", "slot_no"]
        constraints = [
            models.UniqueConstraint(fields=["machine_id", "slot_no"], name="uniq_producto_machine_slot"),
        ]

    def __str__(self) -> str:
        return f"Producto {self.machine_id} slot {self.slot_no} product {self.product_id}"
