from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProgressEntryViewSet, ProgressStatsView, export_progress

router = DefaultRouter()
router.register(r'', ProgressEntryViewSet, basename='progressentry')

urlpatterns = [
    path('', include(router.urls)),  # Inclui as URLs do viewset
    path('stats/', ProgressStatsView.as_view(), name='progress-stats'),  # Estatísticas do progresso
    path('export/', export_progress, name='progress-export'),  # Exportação de progresso
]
