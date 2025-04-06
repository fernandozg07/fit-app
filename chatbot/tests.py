from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from chatbot.models import ChatMessage

class ChatbotTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='chatuser@example.com',
            password='teste123',
            weight=70,
            height=175,
            fitness_goal='ganho muscular'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = '/chat/'

    def test_chatbot_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, {'message': 'Olá'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_chatbot_rejects_empty_message(self):
        response = self.client.post(self.url, {'message': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_chatbot_returns_valid_response(self):
        response = self.client.post(self.url, {'message': 'Preciso de um treino para bíceps'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response', response.data)
        self.assertTrue(len(response.data['response']) > 0)
