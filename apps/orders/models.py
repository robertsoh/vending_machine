from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        DISPENSING = "DISPENSING", "Dispensing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    machine_id = models.CharField(max_length=64, db_index=True)
    trade_no = models.CharField(max_length=32, unique=True, db_index=True)
    slot_number = models.CharField(max_length=32)
    product_id = models.CharField(max_length=32)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
    niubiz_transaction_id = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order#{self.id} {self.trade_no} {self.machine_id} {self.status}"
