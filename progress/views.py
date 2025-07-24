from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Max, Min
from django.http import HttpResponse
from django.utils.dateparse import parse_date
import csv
from datetime import date # Importar date para cálculos

from .models import ProgressEntry
from .serializers import ProgressEntrySerializer
from .permissions import IsOwner # Certifique-se de que IsOwner está definida ou remova se não for usada

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
        user = request.user
        entries = ProgressEntry.objects.filter(user=user).order_by('-date') # Ordena para pegar o mais recente

        current_weight = None
        weight_change = None
        bmi = None

        if entries.exists():
            latest_entry = entries.first()
            current_weight = latest_entry.weight

            # Cálculo de weight_change (exemplo: diferença do peso atual para o primeiro registro)
            first_entry = entries.last() # O mais antigo, já que está ordenado por '-date'
            if first_entry and current_weight is not None:
                weight_change = current_weight - first_entry.weight
            
            # Cálculo de BMI (IMC)
            # Requer a altura do usuário, que deve estar no modelo User
            # Assumindo que user.height está em metros para o cálculo do IMC (peso em kg / altura em metros^2)
            # Se user.height estiver em cm, divida por 100
            if user.height and current_weight is not None and user.height > 0:
                height_in_meters = user.height 
                # Se a altura do usuário estiver em centímetros, use:
                # height_in_meters = user.height / 100 
                bmi = current_weight / (height_in_meters ** 2)


        stats = {
            'total_entries': entries.count(),
            'avg_weight': entries.aggregate(Avg('weight'))['weight__avg'],
            'max_weight': entries.aggregate(Max('weight'))['weight__max'],
            'min_weight': entries.aggregate(Min('weight'))['weight__min'],
            'avg_body_fat': entries.aggregate(Avg('body_fat'))['body_fat__avg'],
            'avg_muscle_mass': entries.aggregate(Avg('muscle_mass'))['muscle_mass__avg'],
            'current_weight': current_weight,
            'weight_change': weight_change,
            'bmi': bmi,
            # Placeholder para estatísticas de treino, que exigem consulta a outros modelos
            'total_workouts': 0, 
            'active_days': 0,
            'average_workout_duration': 0,
            'calories_burned': 0,
        }
        return Response(stats)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_progress(request):
    entries = ProgressEntry.objects.filter(user=request.user).order_by('date')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="progress_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Data', 'Peso (kg)', 'Gordura Corporal (%)', 'Massa Muscular (kg)', 'Observações']) # NOVO: Adicionado 'Observações'

    for entry in entries:
        writer.writerow([
            entry.date,
            entry.weight,
            entry.body_fat if entry.body_fat is not None else '',
            entry.muscle_mass if entry.muscle_mass is not None else '',
            entry.notes if entry.notes is not None else '' # NOVO: Adicionado campo notes
        ])

    return response

