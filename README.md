# EZWare_Backend

Hệ thống quản lý kho (backend API).

## Công nghệ

- Python 3.10+
- Django 5, Django REST Framework
- Token Authentication
- drf-yasg (Swagger UI)
- SQLite

## Cấu trúc CSDL

6 bảng:

- `users` (user_id, username, password, full_name, email, phone, user_role, is_active) — user_role: admin/staff
- `products` (product_id, product_code, product_name, product_type, product_description, is_active) — không lưu đơn giá, product_type lưu text
- `warehouses` (warehouse_id, warehouse_name, warehouse_location, is_active)
- `inventory_receipts` (receipt_id, warehouse_id, receipt_type, receipt_status, created_at) — type: IMPORT/EXPORT, status: PENDING/APPROVED/CANCELLED
- `receipt_details` (detail_id, receipt_id, product_id, quantity) — không lưu đơn giá
- `inventory` — UNIQUE(warehouse_id, product_id), quantity. Tồn kho thực tế, cập nhật khi phiếu APPROVED. (Bảng có cột `id` tự sinh; ràng buộc duy nhất trên cặp warehouse_id + product_id để mỗi SP chỉ có 1 dòng tồn mỗi kho.)

## Cấu trúc thư mục

```
EZWare_Backend/
├── manage.py
├── requirements.txt
├── README.md
├── ezware_postman_collection.json
└── ezware/
    ├── settings.py, urls.py, wsgi.py, asgi.py
    ├── core/        # constants + lệnh import_excel
    ├── accounts/    # Users + Auth
    ├── products/
    ├── warehouses/  # gồm endpoint /<id>/inventory
    ├── inventory/   # InventoryReceipts, ReceiptDetails, Inventory
    └── reports/     # low-stock
```

## Cách chạy

```bash
pip install -r requirements.txt

python manage.py makemigrations accounts products warehouses inventory
python manage.py migrate

# Cách 1: import dữ liệu mẫu từ file Excel kèm theo
python manage.py import_excel EZWare_DuLieuMau.xlsx

# Chạy lại từ đầu (xóa data cũ rồi import lại):
python manage.py import_excel EZWare_DuLieuMau.xlsx --reset

# Cách 2: tự tạo admin để bắt đầu trắng
python manage.py shell -c "from ezware.accounts.models import User; User.objects.create_user(username='admin01', password='123456', user_role='admin', full_name='Quản trị viên')"

python manage.py runserver
```

Tài khoản mẫu (sau khi import Excel):
- admin01 / 123456 (admin)
- nv01, nv02 / 123456 (staff)

## URL

- Swagger UI: http://127.0.0.1:8000/swagger/
- Django admin: http://127.0.0.1:8000/admin/

## Token

Mọi endpoint trừ register / login đều cần header:

```
Authorization: Token <chuỗi-token>
```

## Danh sách API

Auth:
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET, PUT /api/auth/me

Dữ liệu nền (GET cho staff + admin, POST/PUT/DELETE chỉ admin):
- GET, POST /api/products — GET chỉ trả is_active=True
- GET, PUT, DELETE /api/products/<id>
- GET, POST /api/warehouses — GET chỉ trả is_active=True
- GET, PUT, DELETE /api/warehouses/<id>

Vận hành kho:
- POST /api/receipts — tạo phiếu, từ chối nếu kho is_active=False
- POST /api/receipts/<id>/details — thêm chi tiết, từ chối nếu SP is_active=False
- PUT /api/receipts/<id>/status — duyệt/hủy phiếu, chỉ admin

Báo cáo:
- GET /api/warehouses/<id>/inventory — tồn kho 1 kho
- GET /api/reports/low-stock?threshold=10&warehouse_id=1 — sản phẩm tồn dưới ngưỡng

## Luồng phiếu nhập/xuất

1. Tạo phiếu (POST /api/receipts) → trạng thái PENDING. Kho phải đang hoạt động.
2. Thêm chi tiết (POST /api/receipts/<id>/details). Chỉ làm được khi phiếu PENDING, sản phẩm phải đang hoạt động.
3. Duyệt (PUT /api/receipts/<id>/status với body `{"receipt_status":"APPROVED"}`):
   - Phiếu IMPORT: cộng quantity vào bảng inventory.
   - Phiếu EXPORT: kiểm tra inventory.quantity >= detail.quantity, đủ thì trừ, thiếu thì trả về 400.
4. Hủy phiếu (`{"receipt_status":"CANCELLED"}`): chỉ đổi trạng thái, không đụng inventory.

Phần cập nhật tồn kho chạy trong `transaction.atomic()` để rollback khi lỗi.
