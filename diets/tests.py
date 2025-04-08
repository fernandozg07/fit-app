from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from diets.models import Diet
from datetime import timedelta


class DietTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='strongpassword123',
            objetivo='ganho_massa'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_diet(self):
        url = reverse('diet-create')
        data = {
            'calories': 2500,
            'carbohydrates': 300,
            'proteins': 150,
            'fats': 70,
            'meals': 'Café da manhã, almoço e jantar',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Diet.objects.count(), 1)
        self.assertEqual(Diet.objects.first().user, self.user)

    def test_list_user_diets(self):
        Diet.objects.create(user=self.user, calories=2000)
        url = reverse('diet-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_feedback_on_diet(self):
        diet = Diet.objects.create(user=self.user, calories=2000)
        url = reverse('diet-feedback', kwargs={'pk': diet.pk})
        data = {'nota': 4, 'comentarios': 'Boa dieta, só queria mais proteína'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(diet.feedbacks.count(), 1)
