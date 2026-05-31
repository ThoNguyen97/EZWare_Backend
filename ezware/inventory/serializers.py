from rest_framework import serializers
from .models import InventoryReceipt, ReceiptDetail, Inventory


class ReceiptDetailSerializer(serializers.ModelSerializer):
    """Một dòng chi tiết phiếu, kèm thông tin sản phẩm."""
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = ReceiptDetail
        fields = ['detail_id', 'receipt', 'product',
                  'product_code', 'product_name', 'quantity']
        extra_kwargs = {
            'receipt': {'read_only': True},
        }


class InventoryReceiptSerializer(serializers.ModelSerializer):
    """Phiếu nhập / xuất kèm danh sách dòng chi tiết."""
    warehouse_name = serializers.CharField(source='warehouse.warehouse_name', read_only=True)
    details = ReceiptDetailSerializer(many=True, read_only=True)

    class Meta:
        model = InventoryReceipt
        fields = ['receipt_id', 'warehouse', 'warehouse_name',
                  'receipt_type', 'receipt_status',
                  'created_at', 'details']
        read_only_fields = ['receipt_status', 'created_at']


class UpdateStatusSerializer(serializers.Serializer):
    """Body của PUT /api/receipts/<id>/status."""
    receipt_status = serializers.CharField(max_length=15)


class InventorySerializer(serializers.ModelSerializer):
    """Một dòng tồn kho: SP nào + số lượng còn lại."""
    product_id = serializers.IntegerField(source='product.product_id', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_type = serializers.CharField(source='product.product_type', read_only=True)

    class Meta:
        model = Inventory
        fields = ['product_id', 'product_code', 'product_name',
                  'product_type', 'quantity']
