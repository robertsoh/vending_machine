from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditableModel(models.Model):
    class Meta:
        abstract = True


class FeatureFlag(AuditableModel, TimeStampedModel):
    name = models.CharField(max_length=120)
    name_key = models.CharField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name_key}={self.is_active}"

    @classmethod
    def get_feature_flags(cls, name_keys):
        flags = dict(
            cls.objects.filter(name_key__in=name_keys).values_list(
                "name_key", "is_active"
            )
        )
        return {name_key: flags.get(name_key, False) for name_key in name_keys}

    @classmethod
    def get_feature_flag(cls, name_key):
        return cls.get_feature_flags([name_key]).get(name_key, False)
