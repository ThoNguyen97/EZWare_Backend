import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------------------------------------------------
# Cấu hình bảo mật & môi trường: ưu tiên đọc từ biến môi trường (Render, .env),
# có fallback an toàn cho lúc chạy local. Các giá trị fallback CHỈ DÙNG CHO DEV
# — khi deploy production phải set env vars thật trên Render dashboard.
# ----------------------------------------------------------------------------
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-ezware-python')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')

CSRF_TRUSTED_ORIGINS = [
    'https://ezware-backend.onrender.com',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',

    'ezware.core',
    'ezware.accounts',
    'ezware.products',
    'ezware.warehouses',
    'ezware.inventory',
    'ezware.reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # whitenoise: serve static files (CSS/JS của Swagger UI) trên production
    # mà không cần Nginx — đặt ngay sau SecurityMiddleware theo doc whitenoise.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ezware.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ezware.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_USER_MODEL = 'accounts.User'


LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# whitenoise nén + cache-bust static files (CompressedManifestStorage thêm hash
# vào filename, giúp browser cache mãnh liệt mà không sợ stale).
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    # Chỉ dùng TokenAuthentication cho API. KHÔNG bật SessionAuthentication
    # vì nó kích hoạt CSRF check khi browser có sẵn session cookie của Django
    # admin → mọi POST/PUT/DELETE (kể cả /login) sẽ fail với "CSRF token missing".
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
}


SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Nhập theo dạng: Token <key>',
        }
    },
    'USE_SESSION_AUTH': False,
}


LOW_STOCK_THRESHOLD = 10
