from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
)


class RegisterView(APIView):
    """Đăng ký tài khoản mới, trả luôn token để dùng được ngay"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        user = ser.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': UserProfileSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Đăng nhập bằng username + password, trả về token"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        ser = LoginSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        user = ser.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': UserProfileSerializer(user).data,
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Đăng xuất: chỉ xóa token đang dùng cho request hiện tại.

    Trước đây xóa tất cả token của user — gây kick user khỏi mọi thiết bị.
    Giờ chỉ xóa token đính kèm request (request.auth) để các phiên khác
    của cùng user không bị ảnh hưởng. DRF mặc định 1 user 1 token nên
    hành vi vẫn tương đương với trường hợp single-device.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.auth is not None:
            request.auth.delete()
        return Response({'detail': 'Đã đăng xuất'}, status=status.HTTP_200_OK)


class MeView(generics.RetrieveUpdateAPIView):
    """Xem hoặc cập nhật thông tin của chính user đang đăng nhập"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put']

    def get_object(self):
        return self.request.user
