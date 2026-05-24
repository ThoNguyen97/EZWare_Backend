from rest_framework import serializers
from .models import InventoryReceipt, ReceiptDetail, Inventory


class ReceiptDetailSerializer(serializers.ModelSerializer):
    """1 dòng chi tiết phiếu, kèm thông tin sản phẩm.

    `receipt` để read_only — view phải gán qua serializer.save(receipt=phieu),
    chống trường hợp client gửi `receipt` đi kèm để chèn chi tiết sang phiếu khác.
    """
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    # Chặn quantity = 0 ngay từ tầng serializer (PositiveIntegerField cho phép 0)
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = ReceiptDetail
        fields = ['detail_id', 'receipt', 'product',
                  'product_code', 'product_name', 'quantity']
        extra_kwargs = {
            'receipt': {'read_only': True},
        }


class InventoryReceiptSerializer(serializers.ModelSerializer):
    """Phiếu nhập / xuất kèm danh sách dòng chi tiết"""
    warehouse_name = serializers.CharField(source='warehouse.warehouse_name', read_only=True)
    details = ReceiptDetailSerializer(many=True, read_only=True)

    class Meta:
        model = InventoryReceipt
        fields = ['receipt_id', 'warehouse', 'warehouse_name',
                  'receipt_type', 'receipt_status',
                  'created_at', 'details']
        read_only_fields = ['receipt_status', 'created_at']


class UpdateStatusSerializer(serializers.Serializer):
    """Body của PUT /api/receipts/<id>/status - chỉ cần receipt_status"""
    receipt_status = serializers.CharField(max_length=15)


class InventorySerializer(serializers.ModelSerializer):
    """1 dòng tồn kho: SP nào + số lượng còn lại"""
    product_id = serializers.IntegerField(source='product.product_id', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_type = serializers.CharField(source='product.product_type', read_only=True)

    class Meta:
        model = Inventory
        fields = ['product_id', 'product_code', 'product_name',
                  'product_type', 'quantity']
