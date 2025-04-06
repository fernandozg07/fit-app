from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProgressEntryViewSet, ProgressStatsView, export_progress

router = DefaultRouter()
router.register(r'', ProgressEntryViewSet, basename='progressentry')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', ProgressStatsView.as_view(), name='progress-stats'),
    path('export/', export_progress, name='progress-export'),
]
