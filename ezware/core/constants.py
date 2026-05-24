# Vai trò user
ROLE_ADMIN = 'admin'
ROLE_STAFF = 'staff'

ROLE_CHOICES = [
    (ROLE_ADMIN, 'Quản trị viên'),
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
