from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import User

class ChatbotTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='teste@chat.com',
            password='chatpassword',
            fitness_goal='ganho muscular',
            weight=75.0,
            height=1.80,
            birth_date='2000-01-01'
        )
        self.client.force_authenticate(user=self.user)

    def test_enviar_mensagem_para_ia(self):
        data = {"mensagem": "Me recomenda um treino para peito"}
        response = self.client.post('/chatbot/', data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("resposta", response.data)

    def test_mensagem_vazia(self):
        data = {"mensagem": ""}
        response = self.client.post('/chatbot/', data)
        self.assertEqual(response.status_code, 400)
