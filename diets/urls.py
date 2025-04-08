from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DietViewSet,
    WorkoutViewSet,
    generate_diet,
    generate_workout,
    log_workout,
    provide_feedback,
    diet_feedback,
)

router = DefaultRouter()
router.register(r'diets', DietViewSet, basename='diet')
router.register(r'workouts', WorkoutViewSet, basename='workout')

urlpatterns = [
    path('', include(router.urls)),  # Inclui as URLs do viewset
    path('generate-diet/', generate_diet, name='generate_diet'),  # Geração de dieta
    path('generate-workout/', generate_workout, name='generate_workout'),  # Geração de treino
    path('log-workout/', log_workout, name='log_workout'),  # Registro de treino
    path('feedback/', provide_feedback, name='feedback'),  # Feedback de treino
    path('diet-feedback/', diet_feedback, name='diet_feedback'),  # Feedback de dieta
]
