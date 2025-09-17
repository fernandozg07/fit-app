from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.DietViewSet, basename='diet')

urlpatterns = [
    path('generate/', views.generate_diet, name='generate_diet'),
    path('register/', views.register_diet, name='register_diet'),
    path('', include(router.urls)),
]