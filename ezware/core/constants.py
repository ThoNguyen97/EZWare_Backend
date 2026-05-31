# Vai trò user — 3 cấp phản ánh tổ chức quản lý kho thực tế
ROLE_ADMIN = 'admin'        # Quản trị hệ thống — quản lý tài khoản (qua Django admin)
ROLE_MANAGER = 'manager'    # Trưởng kho — mọi nghiệp vụ kho, không quản tài khoản
ROLE_STAFF = 'staff'        # Nhân viên kho — ghi phiếu PENDING, không duyệt

ROLE_CHOICES = [
    (ROLE_ADMIN, 'Quản trị viên'),
    (ROLE_MANAGER, 'Trưởng kho'),
    (ROLE_STAFF, 'Nhân viên kho'),
]


# Loại phiếu: nhập kho hay xuất kho
RECEIPT_TYPE_IMPORT = 'IMPORT'
RECEIPT_TYPE_EXPORT = 'EXPORT'

RECEIPT_TYPE_CHOICES = [
    (RECEIPT_TYPE_IMPORT, 'Nhập kho'),
    (RECEIPT_TYPE_EXPORT, 'Xuất kho'),
]


# Trạng thái phiếu: chờ duyệt / đã duyệt / đã hủy
RECEIPT_STATUS_PENDING = 'PENDING'
RECEIPT_STATUS_APPROVED = 'APPROVED'
RECEIPT_STATUS_CANCELLED = 'CANCELLED'

RECEIPT_STATUS_CHOICES = [
    (RECEIPT_STATUS_PENDING, 'Chờ duyệt'),
    (RECEIPT_STATUS_APPROVED, 'Đã duyệt'),
    (RECEIPT_STATUS_CANCELLED, 'Đã hủy'),
]
