from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import User
from accounts.serializers import UserSerializer

class IsOwner(permissions.BasePermission):
    """
    Permite que apenas o dono do objeto (usuário autenticado) acesse ou edite.
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.user

@api_view(['POST'])
def register_user(request):
    """
    Registra um novo usuário e retorna tokens JWT.
    """
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para o usuário autenticado visualizar/editar seus próprios dados.
    """
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
