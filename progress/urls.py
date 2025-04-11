from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProgressEntryViewSet, ProgressStatsView, export_progress

router = DefaultRouter()
router.register(r'', ProgressEntryViewSet, basename='progressentry')

urlpatterns = [
    path('export/', export_progress, name='progress-export'),
    path('stats/', ProgressStatsView.as_view(), name='progress-stats'),
    path('', include(router.urls)),
]
