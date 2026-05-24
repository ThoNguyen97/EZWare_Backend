from django.db import models


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_code = models.CharField(max_length=50, unique=True)
    product_name = models.CharField(max_length=200)
    product_type = models.CharField(max_length=100, blank=True, default='')
    product_description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return f"{self.product_code} - {self.product_name}"
