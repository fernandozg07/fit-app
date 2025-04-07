from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from accounts.views import register_user, UserViewSet
from django.http import JsonResponse

# 👇 Essa view retorna um JSON básico na rota "/"
def homepage(request):
    return JsonResponse({
        "message": "🚀 API Fitness funcionando com sucesso!",
        "docs": "Acesse /swagger/ para visualizar a documentação da API."
    })

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

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', homepage),  # 👈 ESSA LINHA CRIA A ROTA "/"
    path('admin/', admin.site.urls),

    path('accounts/', include('accounts.urls')),
    path('accounts/', include(router.urls)),
    path('diets/', include('diets.urls')),
    path('workouts/', include('workouts.urls')),
    path('progress/', include('progress.urls')),
    path('chat/', include('chatbot.urls')),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
