from pathlib import Path
from decouple import config
import openai

# Definir a chave da API do OpenAI
openai.api_key = config('OPENAI_API_KEY')

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuração da chave secreta (para uso em produção, altere a chave para algo único)
SECRET_KEY = config('SECRET_KEY')

# Definir se o ambiente está em modo de desenvolvimento ou produção
DEBUG = config('DEBUG', default=True, cast=bool)

# Definir os hosts permitidos (em produção, adicione os domínios permitidos)
ALLOWED_HOSTS = []

# Apps instalados
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Meus apps
    "accounts",
    "workouts",
    "diets",
    'progress',
    'chatbot',

    # Terceiros
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
]

# Configuração de middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL de raiz do projeto
ROOT_URLCONF = 'fitness_app.urls'

# Configuração de templates
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

# Configuração WSGI
WSGI_APPLICATION = 'fitness_app.wsgi.application'

# Configuração do banco de dados (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Validadores de senha
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

# Código de linguagem e fuso horário
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True

# Diretório de arquivos estáticos
STATIC_URL = 'static/'

# Definir o tipo de campo auto-incrementável
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modelo de usuário personalizado
AUTH_USER_MODEL = "accounts.User"

# Configuração do Django Rest Framework e django-filters
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}
