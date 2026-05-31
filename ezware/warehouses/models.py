from django.db import models


class Warehouse(models.Model):
    warehouse_id = models.AutoField(primary_key=True)
    warehouse_code = models.CharField(max_length=50, unique=True)
    warehouse_name = models.CharField(max_length=200, unique=True)
    warehouse_location = models.CharField(max_length=500, blank=True, default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'warehouses'

    def __str__(self):
        return f'{self.warehouse_code} - {self.warehouse_name}'
