from django.db import models


class Machine(models.Model):
    machine_id = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    last_seen_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["machine_id"]

    def __str__(self) -> str:
        return self.machine_id
