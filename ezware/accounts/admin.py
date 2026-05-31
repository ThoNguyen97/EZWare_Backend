from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('user_id', 'username', 'full_name',
                    'user_role', 'is_active', 'is_staff')
    list_filter = ('user_role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'full_name', 'email')
    ordering = ('user_id',)
    readonly_fields = ('last_login',)
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Thông tin cá nhân', {'fields': ('full_name', 'email', 'phone')}),
        ('Vai trò & Trạng thái', {
            'fields': ('user_role', 'is_active', 'is_staff', 'is_superuser'),
        }),
        ('Phân quyền nâng cao', {
            'classes': ('collapse',),
            'fields': ('groups', 'user_permissions'),
        }),
        ('Lịch sử', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2',
                       'full_name', 'email', 'phone', 'user_role'),
        }),
    )
