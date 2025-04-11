from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from diets.models import Diet

class DietTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123',
            objetivo='ganho de massa',  # importante!
            data_nascimento='2000-01-01',
            peso=70,
            altura=175,
            restricoes_alimentares=''
        )
        self.client.force_authenticate(user=self.user)

    def test_generate_diet(self):
        response = self.client.post('/diets/generate/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('meals', response.data)
        self.assertEqual(Diet.objects.count(), 1)

    def test_register_diet(self):
        payload = {
            "meals": {
                "café da manhã": "ovos mexidos e aveia",
                "almoço": "frango grelhado, arroz integral e salada",
                "jantar": "salmão e batata-doce"
            },
            "calorias": 2500
        }
        response = self.client.post('/diets/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Diet.objects.count(), 1)

    def test_send_diet_feedback(self):
        diet = Diet.objects.create(
            user=self.user,
            meals={
                "café da manhã": "ovos mexidos",
                "almoço": "arroz e frango",
                "jantar": "peixe e legumes"
            },
            calorias=2000
        )
        url = f'/diets/{diet.id}/feedback/'
        data = {"nota": 4}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        diet.refresh_from_db()
        self.assertEqual(diet.feedback, 4)

    def test_diet_viewset_feedback_action(self):
        diet = Diet.objects.create(
            user=self.user,
            meals={
                "café da manhã": "iogurte",
                "almoço": "carne com legumes",
                "jantar": "sopa de legumes"
            },
            calorias=1800
        )
        response = self.client.post(f'/diets/{diet.id}/feedback/', {'nota': 5}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        diet.refresh_from_db()
        self.assertEqual(diet.feedback, 5)
