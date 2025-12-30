import sys
import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Проверяем, на Render ли мы
ON_RENDER = 'RENDER' in os.environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ========== БАЗОВЫЕ НАСТРОЙКИ ==========

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# ========== ДЕБАГ ЛОГИ ==========

print("=" * 50, file=sys.stderr)
print(f"ON_RENDER: {ON_RENDER}", file=sys.stderr)
print(f"DATABASE_URL exists: {'DATABASE_URL' in os.environ}", file=sys.stderr)
db_url = os.environ.get('DATABASE_URL')
print(f"DATABASE_URL value: {db_url}", file=sys.stderr)
print(f"DATABASE_URL length: {len(db_url) if db_url else 0}", file=sys.stderr)
print("=" * 50, file=sys.stderr)

# ========== НАСТРОЙКИ БЕЗОПАСНОСТИ ==========

if ON_RENDER:
    # ⚙️ ПРОДАКШЕН НА RENDER
    DEBUG = False  # Выключаем дебаг в продакшн-режиме
    
    # Разрешаем все поддомены render.com
    ALLOWED_HOSTS = [
        '.onrender.com',  # все поддомены .onrender.com
        'localhost',       # для разработки локально
        '127.0.0.1',       # для разработки локально
    ]
    
    # Настройка CSRF доверенных источников
    CSRF_TRUSTED_ORIGINS = [
        'https://*.onrender.com',  # Доверяем поддомены на Render
        'http://localhost:8000',   # Для локальной разработки
        'http://127.0.0.1:8000',   # Для локальной разработки
    ]
    
    # Дополнительные настройки для продакшн:
    # Настройки базы данных, статики, безопасности и т.д.

else:
    # ⚙️ ЛОКАЛЬНАЯ РАЗРАБОТКА
    DEBUG = True  # Включаем дебаг для локальной разработки
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # Только локальные хосты
    
    # Для локальной разработки разрешаем только локальные запросы
    CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']
    
    # Дополнительные настройки для локальной разработки:
    # (Ваши настройки для локального окружения)

# ========== БАЗА ДАННЫХ ==========

# Начальная конфигурация - по умолчанию SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Проверяем DATABASE_URL
database_url = os.environ.get('DATABASE_URL')

if database_url and database_url.strip():
    # Принудительно добавляем префикс postgresql:// если его нет
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        print(f"Fixed database URL: {database_url[:50]}...", file=sys.stderr)
    
    try:
        # Конфигурируем базу данных
        DATABASES['default'] = dj_database_url.parse(database_url, conn_max_age=600)
        print(f"✅ Using PostgreSQL database: {DATABASES['default']['ENGINE']}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error parsing DATABASE_URL: {e}", file=sys.stderr)
        print(f"Keeping SQLite configuration", file=sys.stderr)
else:
    print("ℹ️ DATABASE_URL not found, using SQLite", file=sys.stderr)

print(f"Final DATABASES config: {DATABASES['default']['ENGINE']}", file=sys.stderr)

# ========== СТАТИЧЕСКИЕ ФАЙЛЫ ==========

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Общая конфигурация MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Добавляем whitenoise для всех
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.CustomMiddleware',
]

if ON_RENDER:
    # На Render
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    # Локально
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Медиа файлы
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ========== ОБЩИЕ НАСТРОЙКИ ==========

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

ROOT_URLCONF = 'lk_clone.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'accounts/templates')],
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

WSGI_APPLICATION = 'lk_clone.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Custom user model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Login/Logout redirects
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Логирование
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO' if ON_RENDER else 'DEBUG',
    },
}

print(f"✅ Настройки загружены: {'Render (продакшен)' if ON_RENDER else 'Локальная разработка'}", file=sys.stderr)
print(f"Database engine: {DATABASES['default']['ENGINE']}", file=sys.stderr)
print(f"Debug mode: {DEBUG}", file=sys.stderr)
