from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import User
from accounts.serializers import UserSerializer


# Permissão personalizada para garantir que um usuário só possa acessar seus próprios dados
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


# Função para registrar um novo usuário
@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()  # Cria o usuário
        # Gera o token de acesso e de refresh para o novo usuário
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ViewSet para manipulação do usuário autenticado
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]  # Usa JWT para autenticação
    permission_classes = [IsAuthenticated, IsOwner]  # Exige que o usuário esteja autenticado e seja o proprietário do recurso

    def get_queryset(self):
        # Retorna o usuário autenticado
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        # Retorna o objeto do usuário autenticado
        return self.request.user
