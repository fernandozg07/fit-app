from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import generate_workout, log_workout, provide_feedback, WorkoutViewSet

router = DefaultRouter()
router.register(r'', WorkoutViewSet, basename='workout')

urlpatterns = [
    # Geração automática de treino com base no objetivo
    path('generate/', generate_workout, name='generate_workout'),  # POST /workouts/generate/

    # Registro de treino realizado (log)
    path('log/', log_workout, name='log_workout'),                 # POST /workouts/log/

    # Envio de feedback (treino ou dieta)
    path('feedback/', provide_feedback, name='workout_feedback'), # POST /workouts/feedback/

    # CRUD de treinos (viewset)
    path('', include(router.urls)),                                # GET, POST, PUT, DELETE /workouts/
]
