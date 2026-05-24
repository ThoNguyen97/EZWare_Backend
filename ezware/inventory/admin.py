from django.contrib import admin
from .models import InventoryReceipt, ReceiptDetail, Inventory


class ReceiptDetailInline(admin.TabularInline):
    model = ReceiptDetail
    extra = 0


@admin.register(InventoryReceipt)
class InventoryReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_id', 'warehouse', 'receipt_type', 'receipt_status', 'created_at']
    list_filter = ['receipt_type', 'receipt_status', 'warehouse']
    inlines = [ReceiptDetailInline]


@admin.register(ReceiptDetail)
class ReceiptDetailAdmin(admin.ModelAdmin):
    list_display = ['detail_id', 'receipt', 'product', 'quantity']


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['warehouse', 'product', 'quantity']
    list_filter = ['warehouse']
    search_fields = ['product__product_code', 'product__product_name']
