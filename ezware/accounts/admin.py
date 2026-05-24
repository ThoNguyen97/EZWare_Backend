from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'username', 'full_name', 'user_role', 'is_active']
    list_filter = ['user_role', 'is_active']
    search_fields = ['username', 'full_name', 'email']
