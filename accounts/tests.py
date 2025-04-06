from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationTests(APITestCase):

    def setUp(self):
        self.url = reverse('register_user')
        self.valid_payload = {
            "email": "teste@example.com",
            "password": "senha123",
            "first_name": "João",
            "last_name": "Silva",
            "birth_date": "2000-01-01",
            "weight": 75.0,
            "height": 1.75,
            "fitness_goal": "ganho muscular",
            "dietary_restrictions": "Sem glúten"
        }

    def test_register_valid_user(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access_token', response.data)
        self.assertEqual(response.data['user']['email'], self.valid_payload['email'])

    def test_missing_password(self):
        payload = self.valid_payload.copy()
        payload.pop('password')
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_negative_weight(self):
        payload = self.valid_payload.copy()
        payload['weight'] = -70
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('weight', response.data)

    def test_invalid_fitness_goal(self):
        payload = self.valid_payload.copy()
        payload['fitness_goal'] = 'voar'
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fitness_goal', response.data)

    def test_age_calculation(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_data = response.data['user']
        self.assertIn('age', user_data)
        self.assertIsInstance(user_data['age'], int)
        self.assertGreaterEqual(user_data['age'], 18)
