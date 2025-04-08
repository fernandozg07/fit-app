from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from accounts.views import register_user, UserViewSet
from django.http import JsonResponse

# View para a página inicial
def homepage(request):
    return JsonResponse({
        "message": "🚀 API Fitness funcionando com sucesso!",
        "docs": "Acesse /swagger/ para visualizar a documentação da API."
    })

# Configuração da documentação Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Fitness API",
        default_version='v1',
        description="API de treino e dieta com inteligência artificial",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="suporte@fitnessapp.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Configuração do roteador para as URLs dos usuários
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

# Padrões de URL do projeto
urlpatterns = [
    path('', homepage),  # Página inicial
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # URLs do app 'accounts'
    path('diets/', include('diets.urls')),      # URLs do app 'diets'
    path('workouts/', include('workouts.urls')),  # URLs do app 'workouts'
    path('progress/', include('progress.urls')),  # URLs do app 'progress'
    path('chat/', include('chatbot.urls')),      # URLs do app 'chatbot'
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
