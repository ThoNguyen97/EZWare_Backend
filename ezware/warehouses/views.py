from django.db.models import ProtectedError
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Warehouse
from .serializers import WarehouseSerializer
from ezware.accounts.permissions import IsAdminOrReadOnly


class WarehouseListCreateView(generics.ListCreateAPIView):
    """GET: danh sách kho. POST: tạo kho mới."""
    serializer_class = WarehouseSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Warehouse.objects.filter(is_active=True).order_by('warehouse_id')


class WarehouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Xem / sửa / xóa kho theo warehouse_id."""
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'warehouse_id'
    http_method_names = ['get', 'put', 'delete']

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'detail': 'Kho đang có phiếu nhập/xuất, không thể xóa. '
                           'Hãy đặt is_active=False để tạm ngưng.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class WarehouseInventoryView(APIView):
    """Liệt kê tồn kho thực tế của một kho."""

    def get(self, request, warehouse_id):
        try:
            kho = Warehouse.objects.get(pk=warehouse_id)
        except Warehouse.DoesNotExist:
            return Response(
                {'detail': f'Không tìm thấy kho id={warehouse_id}'},
                status=status.HTTP_404_NOT_FOUND,
            )

        from ezware.inventory.models import Inventory
        from ezware.inventory.serializers import InventorySerializer

        ds_ton = Inventory.objects.select_related('product').filter(
            warehouse_id=warehouse_id,
        ).order_by('-quantity')

        return Response({
            'warehouse': {
                'warehouse_id': kho.warehouse_id,
                'warehouse_code': kho.warehouse_code,
                'warehouse_name': kho.warehouse_name,
                'warehouse_location': kho.warehouse_location,
                'is_active': kho.is_active,
            },
            'total_items': ds_ton.count(),
            'inventory': InventorySerializer(ds_ton, many=True).data,
        }, status=status.HTTP_200_OK)
