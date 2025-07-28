from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/diets', views.DietViewSet) 

urlpatterns = [
    path('', include(router.urls)),
    path('api/diets/generate/', views.generate_diet, name='generate_diet'),
    path('api/diets/register/', views.register_diet, name='register_diet'),
]
