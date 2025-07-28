from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema

from accounts.models import User
from accounts.serializers import UserSerializer

# Permissão personalizada: Garante que um usuário só possa ver/editar seu próprio perfil.
class IsOwner(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o proprietário do objeto o veja/edite.
    """
    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são permitidas para qualquer solicitação GET, HEAD ou OPTIONS.
        # if request.method in permissions.SAFE_METHODS:
        #     return True
        
        # Permissões de escrita só são permitidas para o proprietário do objeto.
        return obj == request.user

# Classe baseada em APIView para registro do usuário
class RegisterUserView(APIView):
    """
    View para registrar um novo usuário.
    Permite acesso a qualquer um (AllowAny).
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserSerializer,
                         responses={201: UserSerializer})
    def post(self, request):
        """
        Cria um novo usuário e retorna seus dados com tokens de acesso e refresh.
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

# ViewSet para o usuário autenticado (gerenciamento do próprio perfil)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que o usuário autenticado possa visualizar e atualizar seu próprio perfil.
    Permite apenas listar (GET), recuperar (GET por ID), atualizar (PUT/PATCH) e excluir (DELETE) o próprio usuário.
    """
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner] # Apenas usuários autenticados e o próprio dono podem acessar

    def get_queryset(self):
        """
        Retorna apenas o usuário autenticado.
        """
        # Garante que o usuário só possa ver seu próprio registro
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        """
        Retorna o objeto do usuário autenticado para operações de detalhe (retrieve, update, destroy).
        """
        # Garante que as operações de detalhe (PUT, PATCH, DELETE) atuem no usuário logado
        return self.request.user

    # Opcional: Se você quiser desabilitar a listagem de todos os usuários
    # def list(self, request, *args, **kwargs):
    #     return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
