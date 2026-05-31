from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from ezware.core.constants import ROLE_STAFF


class RegisterSerializer(serializers.ModelSerializer):
    """Đăng ký tài khoản công khai. Mọi user đăng ký đều có role staff."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['user_id', 'username', 'password', 'email',
                  'full_name', 'phone']
        extra_kwargs = {
            'user_id': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.user_role = ROLE_STAFF
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Đăng nhập bằng username + password."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs.get('username'),
            password=attrs.get('password'),
        )
        if not user:
            raise serializers.ValidationError('Sai tên đăng nhập hoặc mật khẩu')
        if not user.is_active:
            raise serializers.ValidationError('Tài khoản đã bị khóa')

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'full_name',
                  'phone', 'user_role', 'is_active']
        read_only_fields = ['user_id', 'username', 'user_role', 'is_active']
