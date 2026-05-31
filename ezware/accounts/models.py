from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from ezware.core.constants import ROLE_CHOICES, ROLE_STAFF, ROLE_ADMIN


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('username là bắt buộc')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('user_role', 'admin')
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)

    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=200, blank=True, default='')
    email = models.EmailField(max_length=200, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')

    user_role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_STAFF)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.username} ({self.user_role})"

    def save(self, *args, **kwargs):
        # admin thì có quyền vào /admin/, các role khác thì không
        self.is_staff = (self.user_role == ROLE_ADMIN)
        super().save(*args, **kwargs)

    def la_admin(self):
        return self.user_role == ROLE_ADMIN
