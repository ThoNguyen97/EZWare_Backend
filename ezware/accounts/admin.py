from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin cho custom User model.

    Kế thừa DjangoUserAdmin (django.contrib.auth.admin.UserAdmin) để:
      - Tự động HASH password khi tạo / đổi (qua UserCreationForm / UserChangeForm)
      - Có trang riêng "Đổi mật khẩu" cho user đang tồn tại
      - Hỗ trợ Group + Permission widgets

    KHÔNG được kế thừa từ admin.ModelAdmin trống — sẽ làm password lưu plain text
    (admin generic coi password là CharField text thông thường, không invoke
    set_password()), khiến user không thể đăng nhập qua API.
    """

    # Hiển thị danh sách
    list_display = ('user_id', 'username', 'full_name',
                    'user_role', 'is_active', 'is_staff')
    list_filter = ('user_role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'full_name', 'email')
    ordering = ('user_id',)
    readonly_fields = ('last_login',)
    filter_horizontal = ('groups', 'user_permissions')

    # Form khi EDIT user đã tồn tại
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Thông tin cá nhân', {'fields': ('full_name', 'email', 'phone')}),
        ('Vai trò & Trạng thái', {
            'fields': ('user_role', 'is_active', 'is_staff', 'is_superuser'),
        }),
        ('Phân quyền nâng cao (tuỳ chọn)', {
            'classes': ('collapse',),
            'fields': ('groups', 'user_permissions'),
        }),
        ('Lịch sử', {'fields': ('last_login',)}),
    )

    # Form khi ADD user mới — phải có password1 + password2 để hash
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2',
                       'full_name', 'email', 'phone', 'user_role'),
        }),
    )
