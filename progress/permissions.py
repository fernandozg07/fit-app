# progress/permissions.py

from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """
    Permite acesso apenas ao dono do objeto.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
