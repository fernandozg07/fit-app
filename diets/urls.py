from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DietViewSet, generate_diet, register_diet, send_diet_feedback

router = DefaultRouter()
router.register(r'', DietViewSet, basename='diets')

urlpatterns = [
    path('generate/', generate_diet, name='generate_diet'),
    path('register/', register_diet, name='register_diet'),
    path('<int:diet_id>/feedback/', send_diet_feedback, name='send_diet_feedback'),
    path('', include(router.urls)),
]
