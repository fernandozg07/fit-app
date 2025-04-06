from django.test import TestCase
from django.contrib.auth import get_user_model
from workouts.models import Workout
from datetime import timedelta

User = get_user_model()

class WorkoutModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="workoutuser@example.com",
            password="strongpassword"
        )
        self.user.objetivo = "Perder gordura"
        self.user.data_nascimento = "1995-05-15"
        self.user.peso = 80
        self.user.altura = 1.80
        self.user.save()

    def test_create_workout(self):
        workout = Workout.objects.create(
            user=self.user,
            workout_type='musculacao',
            intensity='Alta',
            duration=timedelta(minutes=45),
            exercises="Supino reto, Agachamento livre",
            series_reps="3x12",
            frequency="3x por semana",
            carga=40
        )
        self.assertEqual(str(workout), f"musculacao ({self.user.email})")
