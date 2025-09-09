from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Permissão personalizada para garantir que um usuário só pode acessar seus próprios dados.
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.user
