from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Max, Min
from django.http import HttpResponse
from django.utils.dateparse import parse_date
import csv

from .models import ProgressEntry
from .serializers import ProgressEntrySerializer
from .permissions import IsOwner

class ProgressEntryViewSet(viewsets.ModelViewSet):
    serializer_class = ProgressEntrySerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user
        queryset = ProgressEntry.objects.filter(user=user)

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(date__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(date__lte=parse_date(end_date))

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProgressStatsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entries = ProgressEntry.objects.filter(user=request.user)

        stats = {
            'total_entries': entries.count(),
            'avg_weight': entries.aggregate(Avg('weight'))['weight__avg'],
            'max_weight': entries.aggregate(Max('weight'))['weight__max'],
            'min_weight': entries.aggregate(Min('weight'))['weight__min'],
            'avg_body_fat': entries.aggregate(Avg('body_fat'))['body_fat__avg'],
            'avg_muscle_mass': entries.aggregate(Avg('muscle_mass'))['muscle_mass__avg'],
        }
        return Response(stats)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_progress(request):
    entries = ProgressEntry.objects.filter(user=request.user).order_by('date')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="progress_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Data', 'Peso (kg)', 'Gordura Corporal (%)', 'Massa Muscular (kg)'])

    for entry in entries:
        writer.writerow([
            entry.date,
            entry.weight,
            entry.body_fat if entry.body_fat is not None else '',
            entry.muscle_mass if entry.muscle_mass is not None else ''
        ])

    return response
