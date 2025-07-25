# No seu urls.py (ex: myproject/urls.py ou myapp/urls.py)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views # Certifique-se de que 'views' está importado corretamente

# Se você estiver usando um DefaultRouter para DietViewSet
router = DefaultRouter()
router.register(r'diets', views.DietViewSet)

urlpatterns = [
    path('api/', include(router.urls)), # Inclua as rotas do ViewSet
    path('api/diets/generate/', views.generate_diet, name='generate_diet'),
    path('api/diets/register/', views.register_diet, name='register_diet'), # Se você usa register_diet
    path('api/diets/<int:diet_id>/feedback/', views.send_diet_feedback, name='send_diet_feedback'), # Se você usa send_diet_feedback
    # NOVO ENDPOINT:
    path('api/diets/daily-plans/', views.get_daily_diet_plans, name='get_daily_diet_plans'),
]