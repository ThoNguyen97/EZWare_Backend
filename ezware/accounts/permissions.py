from rest_framework.permissions import BasePermission, SAFE_METHODS

from ezware.core.constants import ROLE_ADMIN, ROLE_MANAGER


# Tập hợp role có "quyền điều hành" (đụng được nghiệp vụ kho + master data).
# Admin còn quyền cao hơn nữa là quản lý tài khoản (chỉ qua Django admin).
MANAGEMENT_ROLES = (ROLE_ADMIN, ROLE_MANAGER)


class IsAdminRole(BasePermission):
    """Chỉ user_role=admin được phép. Hiện tại không view nào dùng — giữ làm
    sẵn cho tương lai (vd: endpoint CRUD users qua REST nếu cần)."""
    message = 'Chỉ Quản trị viên mới được phép thực hiện thao tác này'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'user_role', None) == ROLE_ADMIN


class IsAdminOrManager(BasePermission):
    """Admin hoặc Manager. Dùng cho các action nghiệp vụ kho cấp cao như
    duyệt phiếu / hủy phiếu."""
    message = 'Chỉ Quản trị viên hoặc Trưởng kho mới được phép thực hiện thao tác này'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'user_role', None) in MANAGEMENT_ROLES


class IsAdminOrReadOnly(BasePermission):
    """Đọc cho mọi user đã login. Ghi (POST/PUT/DELETE) chỉ Admin hoặc Manager.

    Dùng cho master data Products / Warehouses: Staff chỉ xem, Manager + Admin
    được thêm/sửa/xoá. Tên class giữ nguyên để tương thích các import cũ;
    semantic vẫn là 'cao cấp thì ghi, còn lại thì đọc'.
    """
    message = 'Chỉ Quản trị viên hoặc Trưởng kho mới được sửa đổi dữ liệu'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return getattr(request.user, 'user_role', None) in MANAGEMENT_ROLES
