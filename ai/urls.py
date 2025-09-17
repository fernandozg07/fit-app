from django.urls import path
from .views import WorkoutView

urlpatterns = [
    path('workout-suggestion/', WorkoutView.as_view(), name='workout_suggestion'),
]