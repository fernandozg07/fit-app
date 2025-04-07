import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from chatbot.models import ChatMessage

@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create_user(email="testuser@example.com", password="testpassword")

@pytest.fixture
def client():
    return APIClient()

def test_chat_ai(client, user):
    client.force_authenticate(user=user)
    
    # Enviar uma mensagem para o chat
    response = client.post('/api/chat/', {'user_message': 'Qual meu peso atual?'})
    
    # Verificar a resposta
    assert response.status_code == 200
    assert 'response' in response.data

    # Verificar se a mensagem foi salva no banco de dados
    assert ChatMessage.objects.count() == 1
