from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from accounts.views import register_user, UserViewSet

# Swagger schema view
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

# Registrar o viewset do usuário
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

# URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),

    # Rotas dos apps
    path('accounts/', include('accounts.urls')),  # suas rotas manuais, ex: register/
    path('accounts/', include(router.urls)),      # rotas automáticas do viewset (users/)
    path('diets/', include('diets.urls')),
    path('workouts/', include('workouts.urls')),
    path('progress/', include('progress.urls')),
    path('chat/', include('chatbot.urls')),

    # Swagger & Redoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
