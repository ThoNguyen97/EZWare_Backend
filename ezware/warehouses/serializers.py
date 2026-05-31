from rest_framework import serializers
from .models import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['warehouse_id', 'warehouse_code', 'warehouse_name',
                  'warehouse_location', 'is_active']
