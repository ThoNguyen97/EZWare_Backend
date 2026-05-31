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
    """POST /api/auth/register - đăng ký tài khoản, trả về token."""
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
    """POST /api/auth/login - đăng nhập bằng username + password, trả về token."""
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
    """Đăng xuất: chỉ xóa token đang dùng cho request hiện tại."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.auth is not None:
            request.auth.delete()
        return Response({'detail': 'Đã đăng xuất'}, status=status.HTTP_200_OK)


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PUT /api/auth/me - xem hoặc cập nhật profile của user đang login."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put']

    def get_object(self):
        return self.request.user
