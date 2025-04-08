from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DietViewSet

router = DefaultRouter()
router.register(r'', DietViewSet, basename='diet')

urlpatterns = [
    path('', include(router.urls)),
]
