from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import generate_workout, register_workout, send_workout_feedback, WorkoutViewSet

router = DefaultRouter()
router.register(r'', WorkoutViewSet, basename='workout')

urlpatterns = [
    path('generate/', generate_workout, name='generate_workout'),
    path('register/', register_workout, name='register_workout'),
    path('feedback/<int:workout_id>/', send_workout_feedback, name='workout_feedback'),
    path('', include(router.urls)),
]
