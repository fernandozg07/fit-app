from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Mude o prefixo do router para algo que não conflite tão diretamente com as views avulsas
# Por exemplo, 'api/diet_entries' se você quiser que as operações CRUD sejam em /api/diet_entries/
# Ou, se o seu ViewSet for realmente para gerenciar "Dietas diárias" (DietDailyPlan), o nome pode ser mais específico.
# Por enquanto, vamos manter 'api/diets' e ajustar as outras.
router.register(r'api/diets', views.DietViewSet) 

urlpatterns = [
    # Coloque as URLs avulsas ANTES do include(router.urls)
    # Isso garante que elas sejam correspondidas primeiro.
    path('api/diets/generate/', views.generate_diet, name='generate_diet'),
    path('api/diets/register/', views.register_diet, name='register_diet'),
    
    # Inclua as URLs do router por último
    path('', include(router.urls)), 
]