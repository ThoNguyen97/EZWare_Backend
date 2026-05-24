from django.db.models import ProtectedError
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer
from ezware.accounts.permissions import IsAdminOrReadOnly


class ProductListCreateView(generics.ListCreateAPIView):
    """GET: danh sách sản phẩm đang dùng. POST: tạo SP mới (chỉ Admin)."""
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        # Chỉ trả các sản phẩm đang còn hoạt động
        return Product.objects.filter(is_active=True).order_by('product_id')


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Xem / sửa / xóa 1 sản phẩm theo product_id"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'product_id'
    http_method_names = ['get', 'put', 'delete']

    def destroy(self, request, *args, **kwargs):
        # SP đã được dùng trong chi tiết phiếu (FK on_delete=PROTECT)
        # => bắt ProtectedError để trả 400 user-friendly.
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'detail': 'Sản phẩm đã được dùng trong phiếu, không thể xóa. '
                           'Hãy đặt is_active=False để tạm ngưng.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
