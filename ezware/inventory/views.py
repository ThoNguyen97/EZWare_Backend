from django.db import transaction
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import InventoryReceipt, ReceiptDetail, Inventory
from .serializers import (
    InventoryReceiptSerializer,
    ReceiptDetailSerializer,
    UpdateStatusSerializer,
)
from ezware.warehouses.models import Warehouse
from ezware.products.models import Product
from ezware.core.constants import (
    RECEIPT_TYPE_IMPORT,
    RECEIPT_TYPE_EXPORT,
    RECEIPT_STATUS_PENDING,
    RECEIPT_STATUS_APPROVED,
    RECEIPT_STATUS_CANCELLED,
)
from ezware.accounts.permissions import IsAdminOrManager


class ReceiptListCreateView(generics.ListCreateAPIView):
    """GET: danh sách phiếu. POST: tạo phiếu nhập/xuất mới ở trạng thái PENDING."""
    queryset = InventoryReceipt.objects.select_related('warehouse').prefetch_related('details')
    serializer_class = InventoryReceiptSerializer

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        # Không cho phép tạo phiếu cho kho đã ngưng hoạt động
        warehouse_obj = ser.validated_data.get('warehouse')
        if not warehouse_obj.is_active:
            return Response(
                {'detail': f'Kho id={warehouse_obj.warehouse_id} đã tạm ngưng'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(ser)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class ReceiptDetailGetView(generics.RetrieveDestroyAPIView):
    """Xem chi tiết 1 phiếu, hoặc xóa phiếu (chỉ khi còn PENDING).

    Quyền xóa phiếu PENDING: mở rộng cho mọi user đã đăng nhập (Staff cũng được)
    — phục vụ trường hợp nhân viên kho lỡ tạo phiếu nhầm cần huỷ trước khi
    duyệt. Phiếu đã APPROVED/CANCELLED thì không xoá được nữa (đã có check
    trong destroy).
    """
    queryset = InventoryReceipt.objects.select_related('warehouse').prefetch_related('details')
    serializer_class = InventoryReceiptSerializer
    lookup_field = 'receipt_id'

    def destroy(self, request, *args, **kwargs):
        phieu = self.get_object()
        if phieu.receipt_status != RECEIPT_STATUS_PENDING:
            return Response(
                {'detail': f'Phiếu ở trạng thái {phieu.receipt_status}, không xóa được'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


class ReceiptDetailAddView(APIView):
    """Thêm chi tiết vào một phiếu đang ở trạng thái PENDING"""

    @swagger_auto_schema(request_body=ReceiptDetailSerializer(many=True))
    def post(self, request, receipt_id):
        try:
            phieu = InventoryReceipt.objects.get(pk=receipt_id)
        except InventoryReceipt.DoesNotExist:
            return Response(
                {'detail': f'Không tìm thấy phiếu id={receipt_id}'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if phieu.receipt_status != RECEIPT_STATUS_PENDING:
            return Response(
                {'detail': f'Phiếu ở trạng thái {phieu.receipt_status}, không thể thêm chi tiết'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # nhận cả 1 dict lẫn list, gửi kiểu nào cũng được
        data = request.data
        if isinstance(data, dict):
            list_input = [data]
        else:
            list_input = list(data)

        product_ids = []
        for item in list_input:
            pid = item.get('product')
            if pid is None:
                return Response(
                    {'detail': "Mỗi dòng phải có field 'product' (product_id)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            product_ids.append(pid)

        # Lọc ra các sản phẩm đã ngưng để báo lỗi
        sp_da_tat = list(
            Product.objects.filter(
                product_id__in=product_ids, is_active=False,
            ).values_list('product_id', flat=True)
        )
        if sp_da_tat:
            return Response(
                {'detail': f'Các sản phẩm sau đang ngừng hoạt động: {sp_da_tat}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Không cần gán item['receipt'] nữa: serializer đã đặt receipt read_only
        # → truyền phiếu qua serializer.save(receipt=phieu) phía dưới.
        ser = ReceiptDetailSerializer(data=list_input, many=True)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        # Bọc atomic để hoặc tất cả dòng được lưu, hoặc không có dòng nào
        # (tránh trường hợp dòng 3/5 fail → phiếu có chi tiết một nửa).
        with transaction.atomic():
            ser.save(receipt=phieu)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class ReceiptUpdateStatusView(APIView):
    """
    Duyệt hoặc hủy phiếu — Admin hoặc Trưởng kho (Manager).
    APPROVED: cộng/trừ tồn kho trong bảng Inventory.
    CANCELLED: chỉ đổi trạng thái, không đụng tồn.
    """
    permission_classes = [IsAdminOrManager]

    @swagger_auto_schema(request_body=UpdateStatusSerializer)
    def put(self, request, receipt_id):
        ser = UpdateStatusSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        new_status = ser.validated_data['receipt_status'].upper()
        if new_status not in [RECEIPT_STATUS_APPROVED, RECEIPT_STATUS_CANCELLED]:
            return Response(
                {'detail': 'receipt_status chỉ nhận APPROVED hoặc CANCELLED'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            phieu = InventoryReceipt.objects.select_related('warehouse').get(pk=receipt_id)
        except InventoryReceipt.DoesNotExist:
            return Response(
                {'detail': f'Không tìm thấy phiếu id={receipt_id}'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if phieu.receipt_status != RECEIPT_STATUS_PENDING:
            return Response(
                {'detail': f'Phiếu đang ở {phieu.receipt_status}, không đổi được nữa'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Hủy phiếu: chỉ đổi trạng thái, không đụng tồn kho
        if new_status == RECEIPT_STATUS_CANCELLED:
            phieu.receipt_status = RECEIPT_STATUS_CANCELLED
            phieu.save(update_fields=['receipt_status'])
            return Response(
                InventoryReceiptSerializer(phieu).data,
                status=status.HTTP_200_OK,
            )

        # Duyệt phiếu
        chi_tiet_list = list(phieu.details.select_related('product').all())
        if not chi_tiet_list:
            return Response(
                {'detail': 'Phiếu chưa có chi tiết, không thể duyệt'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Phiếu xuất: check tồn trước, tránh để DB bị trừ âm
        if phieu.receipt_type == RECEIPT_TYPE_EXPORT:
            for ct in chi_tiet_list:
                ton = Inventory.objects.filter(
                    warehouse=phieu.warehouse_id,
                    product=ct.product_id,
                ).first()

                ton_hien_tai = ton.quantity if ton else 0
                if ton_hien_tai < ct.quantity:
                    return Response({
                        'detail': (
                            f'Không đủ tồn kho cho SP id={ct.product_id} '
                            f'({ct.product.product_name}). '
                            f'Tồn hiện tại: {ton_hien_tai}, cần xuất: {ct.quantity}'
                        )
                    }, status=status.HTTP_400_BAD_REQUEST)
        # TODO: gộp 2 vòng for này lại nếu sau này có thời gian

        with transaction.atomic():
            for ct in chi_tiet_list:
                ton, _ = Inventory.objects.select_for_update().get_or_create(
                    warehouse_id=phieu.warehouse_id,
                    product_id=ct.product_id,
                    defaults={'quantity': 0},
                )

                if phieu.receipt_type == RECEIPT_TYPE_IMPORT:
                    ton.quantity = ton.quantity + ct.quantity
                else:
                    ton.quantity = ton.quantity - ct.quantity

                ton.save(update_fields=['quantity'])

            phieu.receipt_status = RECEIPT_STATUS_APPROVED
            phieu.save(update_fields=['receipt_status'])

        return Response(
            InventoryReceiptSerializer(phieu).data,
            status=status.HTTP_200_OK,
        )
