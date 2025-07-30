from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Importe apenas as views necessárias, 'send_workout_feedback' foi removida
from .views import generate_workout, register_workout, WorkoutViewSet 

router = DefaultRouter()
# O router registrará as rotas para o WorkoutViewSet, incluindo a @action 'feedback'
router.register(r'', WorkoutViewSet, basename='workout')

urlpatterns = [
    # Rotas específicas que não são parte do ViewSet (colocadas primeiro para prioridade)
    path('generate/', generate_workout, name='generate_workout'),
    path('register/', register_workout, name='register_workout'),
    
    # A rota de feedback agora é tratada pela @action no WorkoutViewSet,
    # então esta linha é removida para evitar duplicação ou conflito.
    # path('feedback/<int:workout_id>/', send_workout_feedback, name='workout_feedback'),
    
    # Inclui as rotas geradas pelo router (para o WorkoutViewSet)
    path('', include(router.urls)),
]
