"""
Lệnh import dữ liệu mẫu từ Excel vào DB.
    python manage.py import_excel EZWare_DuLieuMau.xlsx
    python manage.py import_excel EZWare_DuLieuMau.xlsx --reset

Cần: pip install pandas openpyxl
Sheet Inventory được tính lại tự động từ các phiếu APPROVED, không cần điền tay.

--reset: xóa toàn bộ data hiện có trong 6 bảng trước khi import, để chạy
         lại nhiều lần không bị crash do unique constraint (username, product_code…).
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from ezware.accounts.models import User
from ezware.products.models import Product
from ezware.warehouses.models import Warehouse
from ezware.inventory.models import InventoryReceipt, ReceiptDetail, Inventory
from ezware.core.constants import (
    RECEIPT_TYPE_IMPORT,
    RECEIPT_STATUS_APPROVED,
)


def get_val(row, key, default=''):
    val = row.get(key)
    try:
        import pandas as pd
        if pd.isna(val):
            return default
    except Exception:
        pass
    return val if val is not None else default


class Command(BaseCommand):
    help = 'Import dữ liệu từ Excel vào DB'

    def add_arguments(self, parser):
        parser.add_argument('excel_path', type=str)
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Xóa data cũ trong 6 bảng trước khi import (chạy lại nhiều lần).',
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        try:
            import pandas as pd
        except ImportError:
            raise CommandError("Chưa cài pandas. Chạy: pip install pandas openpyxl")

        path = opts['excel_path']
        self.stdout.write(self.style.NOTICE(f"Đang đọc file: {path}"))

        # Xóa data cũ nếu được yêu cầu. Thứ tự xóa quan trọng do ràng buộc FK:
        # Inventory -> ReceiptDetail -> InventoryReceipt -> Warehouse/Product/User
        if opts['reset']:
            self.stdout.write(self.style.WARNING("--reset: đang xóa data cũ..."))
            Inventory.objects.all().delete()
            ReceiptDetail.objects.all().delete()
            InventoryReceipt.objects.all().delete()
            Warehouse.objects.all().delete()
            Product.objects.all().delete()
            # Không xóa superuser (is_superuser=True) để tránh mất tài khoản
            # đang dùng để login admin.
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("  Đã xóa data cũ"))

        # Users
        df = pd.read_excel(path, sheet_name='01_Users')
        count = 0
        for _, r in df.iterrows():
            u = User(
                user_id=int(r['user_id']),
                username=str(r['username']).strip(),
                full_name=str(get_val(r, 'full_name', '')).strip(),
                email=str(get_val(r, 'email', '')).strip(),
                phone=str(get_val(r, 'phone', '')).strip(),
                user_role=str(r['user_role']).strip().lower(),
                is_active=bool(get_val(r, 'is_active', True)),
            )
            u.set_password(str(r['password']))
            u.save()
            count += 1
        self.stdout.write(self.style.SUCCESS(f"  Users: đã nạp {count}"))

        # Products
        df = pd.read_excel(path, sheet_name='02_Products')
        count = 0
        for _, r in df.iterrows():
            Product.objects.create(
                product_id=int(r['product_id']),
                product_code=str(r['product_code']).strip(),
                product_name=str(r['product_name']).strip(),
                product_type=str(get_val(r, 'product_type', '')).strip(),
                product_description=str(get_val(r, 'product_description', '')).strip(),
                is_active=bool(get_val(r, 'is_active', True)),
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"  Products: đã nạp {count}"))

        # Warehouses
        df = pd.read_excel(path, sheet_name='03_Warehouses')
        count = 0
        for _, r in df.iterrows():
            Warehouse.objects.create(
                warehouse_id=int(r['warehouse_id']),
                warehouse_name=str(r['warehouse_name']).strip(),
                warehouse_location=str(get_val(r, 'warehouse_location', '')).strip(),
                is_active=bool(get_val(r, 'is_active', True)),
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"  Warehouses: đã nạp {count}"))

        # Inventory Receipts
        df = pd.read_excel(path, sheet_name='04_InventoryReceipts')
        count = 0
        for _, r in df.iterrows():
            created_at = get_val(r, 'created_at', None)
            if created_at in ('', None) or pd.isna(created_at):
                created_at = None
            else:
                created_at = pd.to_datetime(created_at).to_pydatetime()
                if timezone.is_naive(created_at):
                    created_at = timezone.make_aware(created_at)

            phieu = InventoryReceipt(
                receipt_id=int(r['receipt_id']),
                warehouse_id=int(r['warehouse_id']),
                receipt_type=str(r['receipt_type']).strip().upper(),
                receipt_status=str(r['receipt_status']).strip().upper(),
            )
            phieu.save()
            # created_at có auto_now_add nên phải update sau khi save
            if created_at is not None:
                InventoryReceipt.objects.filter(pk=phieu.pk).update(created_at=created_at)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"  InventoryReceipts: đã nạp {count}"))

        # Receipt Details
        df = pd.read_excel(path, sheet_name='05_ReceiptDetails')
        count = 0
        for _, r in df.iterrows():
            ReceiptDetail.objects.create(
                detail_id=int(r['detail_id']),
                receipt_id=int(r['receipt_id']),
                product_id=int(r['product_id']),
                quantity=int(r['quantity']),
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"  ReceiptDetails: đã nạp {count}"))

        # Dựng lại bảng Inventory từ các phiếu đã duyệt
        # (xóa trắng rồi cộng/trừ lại từ đầu cho chắc)
        self.stdout.write(self.style.NOTICE("  Tính lại bảng Inventory..."))
        Inventory.objects.all().delete()

        approved_receipts = InventoryReceipt.objects.filter(
            receipt_status=RECEIPT_STATUS_APPROVED,
        ).prefetch_related('details')

        for phieu in approved_receipts:
            for ct in phieu.details.all():
                ton, _ = Inventory.objects.get_or_create(
                    warehouse_id=phieu.warehouse_id,
                    product_id=ct.product_id,
                    defaults={'quantity': 0},
                )
                if phieu.receipt_type == RECEIPT_TYPE_IMPORT:
                    ton.quantity += ct.quantity
                else:
                    ton.quantity -= ct.quantity
                ton.save()

        inv_count = Inventory.objects.count()
        self.stdout.write(self.style.SUCCESS(f"  Inventory: đã tạo {inv_count} dòng"))

        self.stdout.write(self.style.SUCCESS("\nIMPORT THÀNH CÔNG"))
