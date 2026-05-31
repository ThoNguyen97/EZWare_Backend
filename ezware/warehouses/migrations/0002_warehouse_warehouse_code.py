"""
Migration thêm cột warehouse_code (UNIQUE, NOT NULL).

Vì DB có thể đang chứa warehouse rows cũ chưa có code, migration thực hiện
3 bước an toàn:
  1. AddField nullable (không UNIQUE) -> SQLite cho phép thêm cột vào table
     có data sẵn.
  2. RunPython: backfill mã 'WH001', 'WH002', ... cho các row đang null.
  3. AlterField: thắt chặt thành unique=True, null=False.

Không reset DB cũng chạy được; chạy fresh DB cũng OK (RunPython skip vì không
có row nào).
"""
from django.db import migrations, models


def backfill_warehouse_code(apps, schema_editor):
    Warehouse = apps.get_model('warehouses', 'Warehouse')
    for w in Warehouse.objects.filter(warehouse_code__isnull=True):
        w.warehouse_code = f'WH{w.warehouse_id:03d}'
        w.save(update_fields=['warehouse_code'])


def reverse_noop(apps, schema_editor):
    # Không cần làm gì khi rollback — DROP COLUMN ở AlterField đảo ngược lại.
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
