from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from workouts.models import Workout, WorkoutLog, WorkoutFeedback
from datetime import timedelta


class WorkoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_workout(self):
        url = reverse('workout-list')  # ViewSet padrão
        data = {
            'workout_type': 'musculacao',
            'intensity': 'moderada',
            'duration': '00:45:00',
            'exercises': 'Supino, Agachamento',
            'series_reps': '3x12',
            'frequency': '3x/semana',
            'carga': 60
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Workout.objects.count(), 1)

    def test_create_workout_log(self):
        workout = Workout.objects.create(
            user=self.user,
            workout_type='musculacao',
            intensity='moderada',
            duration=timedelta(minutes=45)
        )
        log = WorkoutLog.objects.create(workout=workout, nota=5, duracao=45)
        self.assertEqual(WorkoutLog.objects.count(), 1)
        self.assertEqual(log.workout, workout)

    def test_feedback_on_workout_log(self):
        workout = Workout.objects.create(
            user=self.user,
            workout_type='musculacao',
            intensity='alta',
            duration=timedelta(minutes=30)
        )
        log = WorkoutLog.objects.create(workout=workout, nota=4, duracao=30)
        feedback = WorkoutFeedback.objects.create(user=self.user, workout_log=log, rating=5)
        self.assertEqual(WorkoutFeedback.objects.count(), 1)
        self.assertEqual(feedback.user, self.user)
