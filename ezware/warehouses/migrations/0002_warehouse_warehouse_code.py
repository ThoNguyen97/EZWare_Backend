from django.db import migrations, models


def backfill_warehouse_code(apps, schema_editor):
    Warehouse = apps.get_model('warehouses', 'Warehouse')
    for w in Warehouse.objects.filter(warehouse_code__isnull=True):
        w.warehouse_code = f'WH{w.warehouse_id:03d}'
        w.save(update_fields=['warehouse_code'])


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouse',
            name='warehouse_code',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.RunPython(backfill_warehouse_code, reverse_noop),
        migrations.AlterField(
            model_name='warehouse',
            name='warehouse_code',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
