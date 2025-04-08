from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import generate_workout, log_workout, provide_feedback, WorkoutViewSet

router = DefaultRouter()
router.register(r'', WorkoutViewSet, basename='workout')

urlpatterns = [
    path('generate/', generate_workout, name='generate_workout'),  # Geração de treino
    path('log/', log_workout, name='log_workout'),  # Log de treino
    path('feedback/', provide_feedback, name='workout_feedback'),  # Feedback de treino
    path('', include(router.urls)),  # CRUD de treinos
]
