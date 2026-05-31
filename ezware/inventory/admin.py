from django.contrib import admin
from .models import InventoryReceipt, ReceiptDetail, Inventory


class ReceiptDetailInline(admin.TabularInline):
    model = ReceiptDetail
    extra = 0
    autocomplete_fields = ['product']


@admin.register(InventoryReceipt)
class InventoryReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_id', 'warehouse', 'receipt_type', 'receipt_status', 'created_at']
    list_filter = ['receipt_type', 'receipt_status', 'warehouse']
    # Tìm theo mã phiếu, mã/tên kho, mã/tên sản phẩm có trong phiếu
    search_fields = [
        'receipt_id',
        'warehouse__warehouse_code',
        'warehouse__warehouse_name',
        'details__product__product_code',
        'details__product__product_name',
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_select_related = ['warehouse']
    list_per_page = 25
    autocomplete_fields = ['warehouse']
    inlines = [ReceiptDetailInline]


@admin.register(ReceiptDetail)
class ReceiptDetailAdmin(admin.ModelAdmin):
    list_display = ['detail_id', 'receipt', 'product', 'quantity']
    list_filter = ['receipt__receipt_type', 'receipt__receipt_status']
    search_fields = [
        'receipt__receipt_id',
        'product__product_code',
        'product__product_name',
    ]
    list_select_related = ['receipt', 'product']
    autocomplete_fields = ['receipt', 'product']


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['warehouse', 'product', 'quantity']
    list_filter = ['warehouse']
    search_fields = [
        'warehouse__warehouse_code',
        'warehouse__warehouse_name',
        'product__product_code',
        'product__product_name',
    ]
    list_select_related = ['warehouse', 'product']
    autocomplete_fields = ['warehouse', 'product']
    ordering = ['-quantity']
