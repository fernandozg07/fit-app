from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Se você estiver usando um DefaultRouter para DietViewSet
router = DefaultRouter()
router.register(r'api/diets', views.DietViewSet) # Registra o ViewSet sob 'api/diets'

urlpatterns = [
    # Inclui as rotas geradas pelo router (e.g., /api/diets/, /api/diets/{id}/)
    path('', include(router.urls)),
    
    # As funções generate_diet, register_diet e get_daily_diet_plans
    # agora são incluídas AQUI, sem o prefixo 'diets/',
    # pois o urls.py principal já adicionará 'diets/'
    path('api/diets/generate/', views.generate_diet, name='generate_diet'),
    path('api/diets/register/', views.register_diet, name='register_diet'),
    path('api/diets/daily-plans/', views.get_daily_diet_plans, name='get_daily_diet_plans'),
]
