# fitness_app/settings.py

import os
from pathlib import Path
from datetime import timedelta
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------
# Segurança
# -------------------------
SECRET_KEY = config("SECRET_KEY", default="django-insecure-railway-temp-key-12345")
DEBUG = config("DEBUG", default=True, cast=bool)  # Temporariamente True para debug
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*").split(",")

# -------------------------
# Aplicações
# -------------------------
INSTALLED_APPS = [
    # Django padrão
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Terceiros
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_yasg",
    "django_filters",
    "django_extensions",
    "corsheaders",

    # Apps do projeto
    "accounts",
    "diets",
    "workouts",
    "progress",
    "chatbot",
    "ai",
]

# -------------------------
# Middleware
# -------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",    # Deve ser o primeiro
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -------------------------
# URLs e WSGI
# -------------------------
ROOT_URLCONF = "fitness_app.urls"
WSGI_APPLICATION = "fitness_app.wsgi.application"

# -------------------------
# Templates
# -------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# -------------------------
# Banco de Dados
# -------------------------
# Configuração de banco de dados
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL and 'postgres' in DATABASE_URL:
    # PostgreSQL para produção (Railway) - apenas se DATABASE_URL for válida
    try:
        DATABASES = {
            "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
        }
    except Exception:
        # Fallback para SQLite se houver erro na configuração do PostgreSQL
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }
else:
    # SQLite para desenvolvimento local ou fallback
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Configuração adicional para Railway
if 'RAILWAY_ENVIRONMENT' in os.environ or 'RAILWAY_PROJECT_ID' in os.environ:
    # Configurações específicas do Railway
    ALLOWED_HOSTS.extend([
        'web-production-567f4.up.railway.app',
        '.railway.app',
        '.up.railway.app',
        '*'  # Permite qualquer host em produção Railway
    ])
    
    # Força HTTPS em produção
    SECURE_SSL_REDIRECT = False  # Desabilitado temporariamente para debug
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Debug temporário para Railway
    DEBUG = True


# -------------------------
# Usuário customizado
# -------------------------
AUTH_USER_MODEL = "accounts.User"

# -------------------------
# Validação de Senhas
# -------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------
# Internacionalização
# -------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# -------------------------
# Arquivos Estáticos
# -------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------
# Django REST Framework
# -------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
}

# -------------------------
# JWT
# -------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# -------------------------
# Swagger / Redoc
# -------------------------
SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        }
    },
}
REDOC_SETTINGS = {
    "LAZY_RENDERING": False,
}

# -------------------------
# CORS
# -------------------------
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000"
).split(",")]

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False

# -------------------------
# Produção segura
# -------------------------
# Configurações de segurança para produção
if not DEBUG or 'RAILWAY_ENVIRONMENT' in os.environ:
    CSRF_TRUSTED_ORIGINS = [
        "https://web-production-567f4.up.railway.app",
        "https://*.railway.app",
        "https://*.up.railway.app",
    ]
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
