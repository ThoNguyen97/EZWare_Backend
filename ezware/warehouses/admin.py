from django.contrib import admin
from .models import Warehouse


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['warehouse_id', 'warehouse_code', 'warehouse_name',
                    'warehouse_location', 'is_active']
    list_filter = ['is_active']
    search_fields = ['warehouse_code', 'warehouse_name', 'warehouse_location']
