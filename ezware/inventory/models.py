from django.db import models

from ezware.warehouses.models import Warehouse
from ezware.products.models import Product
from ezware.core.constants import (
    RECEIPT_TYPE_CHOICES,
    RECEIPT_STATUS_CHOICES,
    RECEIPT_STATUS_PENDING,
)


class InventoryReceipt(models.Model):
    """Header phiếu nhập / xuất kho"""
    receipt_id = models.AutoField(primary_key=True)

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        db_column='warehouse_id',
        related_name='receipts',
    )

    receipt_type = models.CharField(max_length=10, choices=RECEIPT_TYPE_CHOICES)

    receipt_status = models.CharField(
        max_length=15,
        choices=RECEIPT_STATUS_CHOICES,
        default=RECEIPT_STATUS_PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventory_receipts'
        ordering = ['-created_at']

    def __str__(self):
        return f"Phiếu #{self.receipt_id} ({self.receipt_type}) - {self.receipt_status}"


class ReceiptDetail(models.Model):
    """Từng dòng sản phẩm trong 1 phiếu nhập / xuất"""
    detail_id = models.AutoField(primary_key=True)

    receipt = models.ForeignKey(
        InventoryReceipt,
        on_delete=models.CASCADE,
        db_column='receipt_id',
        related_name='details',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        db_column='product_id',
    )
    quantity = models.PositiveIntegerField()

    class Meta:
        db_table = 'receipt_details'

    def __str__(self):
        return f"Phiếu #{self.receipt_id} - SP {self.product_id} x {self.quantity}"


class Inventory(models.Model):
    """Bảng tổng hợp tồn kho thực tế của từng sản phẩm tại từng kho"""
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        db_column='warehouse_id',
        related_name='inventory',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column='product_id',
        related_name='inventory',
    )
    quantity = models.IntegerField(default=0)

    class Meta:
        db_table = 'inventory'
        # Cặp (warehouse, product) là khóa chính phức hợp
        unique_together = [('warehouse', 'product')]
        indexes = [
            models.Index(fields=['warehouse', 'product']),
        ]

    def __str__(self):
        return f"Kho {self.warehouse_id} - SP {self.product_id}: {self.quantity}"
