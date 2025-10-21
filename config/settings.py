import os
from datetime import timedelta
from pathlib import Path

# Bazaviy katalog
BASE_DIR = Path(__file__).resolve().parent.parent

# Xavfsizlik sozlamalari
SECRET_KEY = 'django-insecure-&#pq=w6+w)7u=iv5t0m+1foi7-afbongg9nk*$b)dm6b0lua2x'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Loyihadagi ilovalar
INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # External libraries
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
    'django_filters',

    # Custom apps
    'users',
    'products',
    'favorites',
    'orders',
]

# Middlewarelar ketma-ketligi
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL konfiguratsiyasi
ROOT_URLCONF = 'config.urls'

# Template konfiguratsiyasi
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Agar custom template papkasi bo‘lsa, shu yerga qo‘shiladi
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI konfiguratsiyasi
WSGI_APPLICATION = 'config.wsgi.application'

# Ma'lumotlar bazasi
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smart',  # PostgreSQL bazasi nomi
        'USER': 'user_smart',  # PostgreSQL foydalanuvchi nomi
        'PASSWORD': 'password_smart',  # PostgreSQL paroli
        'HOST': 'smart_db',  # Docker Compose'dagi konteyner nomi
        'PORT': '5432',  # PostgreSQL uchun standart port
    }
}

# Parol validatsiyasi
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Custom foydalanuvchi modeli
AUTH_USER_MODEL = 'users.User'

# DRF konfiguratsiyasi
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

# JWT token sozlamalari
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=365 * 100),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=365 * 100),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
}

# Lokalizatsiya va vaqt zonasi
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Statik va media fayllar
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key turi
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email konfiguratsiyasi
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your@gmail.com' # O'zingizni gmail manzilingiz.
EMAIL_HOST_PASSWORD = 'your_password' # Gmail manzilingiz ichida app password yaratib joylang.
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
