from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import User
from workouts.models import Workout

class WorkoutTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='teste@teste.com',
            password='testpassword',
            fitness_goal='ganho muscular',
            weight=70.0,
            height=1.75,
            birth_date='2000-01-01'
        )
        self.client.force_authenticate(user=self.user)

    def test_criar_workout_manual(self):
        data = {
            "exercicio": "Supino",
            "series": 4,
            "repeticoes": 10,
            "carga": 60,
            "duracao": 30
        }
        response = self.client.post('/workouts/', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Workout.objects.count(), 1)

    def test_gerar_workout_automatico(self):
        response = self.client.post('/workouts/gerar_automatico/')
        self.assertEqual(response.status_code, 201)
        self.assertGreaterEqual(len(response.data), 1)
