from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Max, Min, Sum
from django.http import HttpResponse
from django.utils.dateparse import parse_date
import csv
from datetime import date, timedelta

from .models import ProgressEntry
from .serializers import ProgressEntrySerializer
# Importar modelos de outras apps para estatísticas
from workouts.models import WorkoutLog, Workout
from diets.models import ConsumedMealLog # AGORA ConsumedMealLog DEVE EXISTIR
from accounts.models import User

# Permissão IsOwner - Certifique-se de que esta classe está definida em progress/permissions.py
# Exemplo de IsOwner (se não tiver):
# from rest_framework import permissions
# class IsOwner(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return obj.user == request.user

# Placeholder para IsOwner se não estiver em um arquivo separado
try:
    from .permissions import IsOwner
except ImportError:
    class IsOwner(IsAuthenticated): # Fallback para IsAuthenticated se IsOwner não for encontrada
        def has_object_permission(self, request, view, obj):
            return obj.user == request.user


class ProgressEntryViewSet(viewsets.ModelViewSet):
    serializer_class = ProgressEntrySerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user
        queryset = ProgressEntry.objects.filter(user=user)

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            parsed_start_date = parse_date(start_date)
            if parsed_start_date:
                queryset = queryset.filter(date__gte=parsed_start_date)
            else:
                raise ValueError("Formato de data de início inválido.")
        if end_date:
            parsed_end_date = parse_date(end_date)
            if parsed_end_date:
                queryset = queryset.filter(date__lte=parsed_end_date)
            else:
                raise ValueError("Formato de data de fim inválido.")

        return queryset.order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProgressStatsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        entries = ProgressEntry.objects.filter(user=user).order_by('-date')

        current_weight = None
        initial_weight = None
        weight_change = None
        bmi = None

        if entries.exists():
            latest_entry = entries.first()
            current_weight = latest_entry.weight
            
            first_entry = entries.last()
            initial_weight = first_entry.weight
            if first_entry and current_weight is not None and first_entry.weight is not None:
                weight_change = current_weight - first_entry.weight
            
            if user.height and current_weight is not None and user.height > 0:
                height_in_meters = user.height / 100.0
                bmi = current_weight / (height_in_meters ** 2)
                bmi = round(bmi, 2)

        # --- Estatísticas de Treino (População Real) ---
        total_workouts = WorkoutLog.objects.filter(workout__user=user).count()
        
        active_days = WorkoutLog.objects.filter(workout__user=user).values('created_at__date').distinct().count()

        avg_workout_duration_agg = WorkoutLog.objects.filter(workout__user=user).aggregate(Avg('duracao'))
        average_workout_duration = avg_workout_duration_agg['duracao__avg'] if avg_workout_duration_agg['duracao__avg'] is not None else 0
        average_workout_duration = round(average_workout_duration, 1)

        calories_burned_total = 0 # Placeholder, ajuste se tiver campo no WorkoutLog

        # Calorias consumidas (AGORA ConsumedMealLog DEVE FUNCIONAR)
        total_calories_consumed_agg = ConsumedMealLog.objects.filter(user=user).aggregate(Sum('calories_consumed'))
        calories_consumed_total = total_calories_consumed_agg['calories_consumed__sum'] if total_calories_consumed_agg['calories_consumed__sum'] is not None else 0


        stats = {
            'total_entries': entries.count(),
            'avg_weight': round(entries.aggregate(Avg('weight'))['weight__avg'] or 0, 2),
            'max_weight': entries.aggregate(Max('weight'))['weight__max'],
            'min_weight': entries.aggregate(Min('weight'))['weight__min'],
            'avg_body_fat': round(entries.aggregate(Avg('body_fat'))['body_fat__avg'] or 0, 2),
            'avg_muscle_mass': round(entries.aggregate(Avg('muscle_mass'))['muscle_mass__avg'] or 0, 2),
            'current_weight': current_weight,
            'initial_weight': initial_weight,
            'weight_change': round(weight_change, 2) if weight_change is not None else None,
            'bmi': bmi,
            'total_workouts': total_workouts, 
            'active_days': active_days,
            'average_workout_duration': average_workout_duration,
            'calories_burned_total': calories_burned_total,
            'calories_consumed_total': calories_consumed_total,
        }
        return Response(stats)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_progress(request):
    entries = ProgressEntry.objects.filter(user=request.user).order_by('date')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="progress_data.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Data', 'Peso (kg)', 'Gordura Corporal (%)', 'Massa Muscular (kg)', 
        'Braço (cm)', 'Peito (cm)', 'Cintura (cm)', 'Quadril (cm)', 
        'Coxa (cm)', 'Panturrilha (cm)', 'Observações'
    ])

    for entry in entries:
        writer.writerow([
            entry.date.isoformat(),
            entry.weight,
            entry.body_fat if entry.body_fat is not None else '',
            entry.muscle_mass if entry.muscle_mass is not None else '',
            entry.arm_circumference if entry.arm_circumference is not None else '',
            entry.chest_circumference if entry.chest_circumference is not None else '',
            entry.waist_circumference if entry.waist_circumference is not None else '',
            entry.hip_circumference if entry.hip_circumference is not None else '',
            entry.thigh_circumference if entry.thigh_circumference is not None else '',
            entry.calf_circumference if entry.calf_circumference is not None else '',
            entry.notes if entry.notes is not None else ''
        ])

    return response
