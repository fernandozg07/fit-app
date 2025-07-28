from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Página inicial
def homepage(request):
    return JsonResponse({
        "message": "🚀 API Fitness funcionando com sucesso!",
        "docs": "Acesse /swagger/ para visualizar a documentação da API."
    })

# Swagger/OpenAPI config
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

# Importar o router da sua aplicação diets
# from diets.urls import router as diets_router # Não precisamos importar o router aqui se ele for incluído
# from diets import views as diets_views # Não precisamos importar views para funções específicas aqui

urlpatterns = [
    path('', homepage),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    
    # Inclui TODAS as rotas definidas em diets/urls.py sob o prefixo 'diets/'
    path('diets/', include('diets.urls')), 
    
    # REMOVIDAS as rotas específicas de dieta daqui, pois agora estão em diets/urls.py
    # path('diets/api/diets/generate/', diets_views.generate_diet, name='generate_diet'),
    # path('diets/api/diets/register/', diets_views.register_diet, name='register_diet'),
    # path('diets/api/diets/daily-plans/', diets_views.get_daily_diet_plans, name='get_daily_diet_plans'),
    
    path('workouts/', include('workouts.urls')),
    path('progress/', include('progress.urls')),
    path('chat/', include('chatbot.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
