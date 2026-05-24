from rest_framework.permissions import BasePermission, SAFE_METHODS

from ezware.core.constants import ROLE_ADMIN


class IsAdminRole(BasePermission):
    """Chỉ user_role=admin được phép"""
    message = 'Chỉ Quản trị viên mới được phép thực hiện thao tác này'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'user_role', None) == ROLE_ADMIN


class IsAdminOrReadOnly(BasePermission):
    """Đọc thì cho mọi user đã login, ghi thì chỉ Admin"""
    message = 'Chỉ Quản trị viên mới được sửa đổi dữ liệu'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return getattr(request.user, 'user_role', None) == ROLE_ADMIN
