from django.db import migrations, models
from django.utils import timezone


def fill_trade_no(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    for order in Order.objects.filter(trade_no__isnull=True).order_by("id"):
        # Include ID suffix to keep existing rows unique.
        order.trade_no = f"{timezone.now().strftime('%Y%m%d%H%M%S%f')}{order.id % 1_000_000:06d}"
        order.save(update_fields=["trade_no"])


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="trade_no",
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True),
        ),
        migrations.RunPython(fill_trade_no, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="order",
            name="trade_no",
            field=models.CharField(db_index=True, max_length=32, unique=True),
        ),
    ]
