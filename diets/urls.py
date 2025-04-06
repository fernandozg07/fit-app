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
    path('', include(router.urls)),
    path('generate-diet/', generate_diet, name='generate_diet'),
    path('generate-workout/', generate_workout, name='generate_workout'),
    path('log-workout/', log_workout, name='log_workout'),
    path('feedback/', provide_feedback, name='feedback'),
    path('diet-feedback/', diet_feedback, name='diet_feedback'),
]
