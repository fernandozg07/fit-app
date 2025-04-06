# accounts/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from accounts.serializers import UserSerializer
from accounts.permissions import IsOwner  # Certifique-se de que está importado corretamente

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwner]  # Aplique a permissão personalizada
