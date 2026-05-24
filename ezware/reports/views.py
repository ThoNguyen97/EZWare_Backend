from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ezware.inventory.models import Inventory


class LowStockReportView(APIView):
    """Cảnh báo các sản phẩm có tồn kho dưới ngưỡng (mặc định 10)"""

    def get(self, request):
        threshold_str = request.query_params.get(
            'threshold',
            str(settings.LOW_STOCK_THRESHOLD),
        )
        try:
            threshold = int(threshold_str)
        except ValueError:
            return Response(
                {'detail': 'threshold phải là số nguyên'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        warehouse_id_str = request.query_params.get('warehouse_id', None)

        # quantity < threshold thì coi là sắp hết
        qs = Inventory.objects.select_related('warehouse', 'product').filter(
            quantity__lt=threshold,
        )
        if warehouse_id_str:
            try:
                qs = qs.filter(warehouse_id=int(warehouse_id_str))
            except ValueError:
                return Response(
                    {'detail': 'warehouse_id phải là số nguyên'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        qs = qs.order_by('quantity')

        items = []
        for inv in qs:
            items.append({
                'warehouse_id': inv.warehouse_id,
                'warehouse_name': inv.warehouse.warehouse_name,
                'product_id': inv.product_id,
                'product_code': inv.product.product_code,
                'product_name': inv.product.product_name,
                'product_type': inv.product.product_type,
                'quantity': inv.quantity,
            })

        return Response({
            'threshold': threshold,
            'total': len(items),
            'items': items,
        }, status=status.HTTP_200_OK)
