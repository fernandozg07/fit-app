# accounts/tests.py
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from accounts.models import User

class UserRegistrationTest(APITestCase):
    def test_user_can_register_without_token(self):
        url = reverse('register_user')
        data = {
            "email": "novo@teste.com",
            "password": "senha123",
            "first_name": "João",
            "last_name": "Silva",
            "birth_date": "2000-01-01",
            "weight": 70,
            "height": 1.75,
            "fitness_goal": "ganho_muscular",
            "dietary_restrictions": "sem lactose"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertTrue(User.objects.filter(email="novo@teste.com").exists())
