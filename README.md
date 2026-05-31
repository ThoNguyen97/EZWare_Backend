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

- `users` (user_id, username, password, full_name, email, phone, user_role, is_active, is_staff, last_login) — user_role: **admin / manager / staff**
- `products` (product_id, product_code, product_name, product_type, product_description, is_active) — không lưu đơn giá, product_type lưu text
- `warehouses` (warehouse_id, warehouse_code, warehouse_name, warehouse_location, is_active) — warehouse_code UNIQUE, do người dùng tự đặt
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

## Cách chạy ở local

Có 2 file requirements:

- `requirements.txt` — production deps (Django, DRF, drf-yasg, gunicorn, whitenoise). Render đọc file này.
- `requirements-dev.txt` — kèm thêm pandas + openpyxl để chạy được lệnh `import_excel` ở local.

```bash
# Cài đặt: dùng -dev nếu muốn import data mẫu từ Excel
pip install -r requirements-dev.txt

python manage.py makemigrations accounts products warehouses inventory
python manage.py migrate

# Tạo tài khoản superadmin đầu tiên (gõ username/password tuỳ ý khi được hỏi)
python manage.py createsuperuser

# (Tùy chọn) Nạp dữ liệu mẫu nghiệp vụ kho: products, warehouses, phiếu, tồn kho
# Lệnh này KHÔNG tạo tài khoản — chỉ data nghiệp vụ.
python manage.py import_excel EZWare_DuLieuMau.xlsx

# Chạy lại từ đầu nếu cần (giữ nguyên user superadmin):
python manage.py import_excel EZWare_DuLieuMau.xlsx --reset

python manage.py runserver
```

## Deploy lên Render

1. Push repo lên GitHub.
2. Tạo Web Service trên https://render.com, kết nối repo.
3. Cấu hình:
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
   - **Start Command**: `gunicorn ezware.wsgi:application`
4. Environment Variables (Settings → Environment):
   | Key | Value |
   |---|---|
   | `DJANGO_SECRET_KEY` | Bấm nút "Generate" để random |
   | `DJANGO_DEBUG` | `False` |
   | `DJANGO_ALLOWED_HOSTS` | `<tên-app>.onrender.com` |

> Lưu ý: SQLite trên Render free tier sẽ reset mỗi lần deploy vì filesystem ephemeral. Cho đồ án demo dùng được; production cần đổi sang Postgres managed của Render.

## Quản lý tài khoản

Hệ thống KHÔNG seed sẵn bất kỳ tài khoản nào. Quy trình tạo tài khoản:

1. Tạo superadmin duy nhất bằng `python manage.py createsuperuser` (Django built-in).
2. Login `/admin/` với superadmin đó.
3. Vào mục **Users → Add User** trên Django admin để tạo các tài khoản còn lại,
   chọn `user_role` phù hợp: `admin` / `manager` / `staff`.
4. Cột `is_staff` (Django default) được tự đồng bộ với `user_role` qua
   `User.save()` — chỉ user role admin mới được phép vào lại `/admin/`.

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

Dữ liệu nền (GET cho mọi user đăng nhập; POST/PUT/DELETE: Admin + Manager):
- GET, POST /api/products — GET chỉ trả is_active=True
- GET, PUT, DELETE /api/products/<id>
- GET, POST /api/warehouses — GET chỉ trả is_active=True
- GET, PUT, DELETE /api/warehouses/<id>

Vận hành kho:
- POST /api/receipts — tạo phiếu (mọi user đăng nhập), từ chối nếu kho is_active=False
- POST /api/receipts/<id>/details — thêm chi tiết (mọi user đăng nhập), từ chối nếu SP is_active=False
- DELETE /api/receipts/<id> — xóa phiếu PENDING (mọi user đăng nhập)
- PUT /api/receipts/<id>/status — duyệt/hủy phiếu (Admin hoặc Manager)

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
