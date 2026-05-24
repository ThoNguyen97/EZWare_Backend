from django.db import models


class Warehouse(models.Model):
    warehouse_id = models.AutoField(primary_key=True)
    warehouse_name = models.CharField(max_length=200, unique=True)
    warehouse_location = models.CharField(max_length=500, blank=True, default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'warehouses'

    def __str__(self):
        return self.warehouse_name
