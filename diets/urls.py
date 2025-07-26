from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Se você estiver usando um DefaultRouter para DietViewSet
router = DefaultRouter()
router.register(r'api/diets', views.DietViewSet) # Registra o ViewSet sob 'api/diets'

urlpatterns = [
    # As rotas geradas pelo router serão:
    # /api/diets/ (GET para listar, POST para criar)
    # /api/diets/{id}/ (GET para detalhe, PUT, PATCH, DELETE)
    # /api/diets/{id}/feedback/ (POST para feedback)
    path('', include(router.urls)),
    
    # As funções generate_diet, register_diet e get_daily_diet_plans
    # serão incluídas diretamente no urls.py principal do projeto,
    # com o prefixo 'diets/' já aplicado.
    # Exemplo (se fossem incluídas aqui):
    # path('api/diets/generate/', views.generate_diet, name='generate_diet'),
    # path('api/diets/register/', views.register_diet, name='register_diet'),
    # path('api/diets/daily-plans/', views.get_daily_diet_plans, name='get_daily_diet_plans'),
]
