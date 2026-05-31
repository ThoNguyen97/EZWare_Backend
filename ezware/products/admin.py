from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'product_code', 'product_name', 'product_type', 'is_active']
    list_filter = ['product_type', 'is_active']
    search_fields = ['product_code', 'product_name', 'product_description']
    ordering = ['product_id']
    list_per_page = 25
