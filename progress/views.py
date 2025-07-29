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
from .serializers import ProgressEntrySerializer, ProgressStatsSerializer # Importe ProgressStatsSerializer
# Importar modelos de outras apps para estatísticas
from workouts.models import WorkoutLog, Workout
from diets.models import ConsumedMealLog
from accounts.models import User

# Permissão IsOwner - Certifique-se de que esta classe está definida em progress/permissions.py
# Se você tiver um arquivo `permissions.py` dentro da sua app `progress`, use-o.
# Caso contrário, este fallback simples será usado.
try:
    from .permissions import IsOwner
except ImportError:
    # Fallback simples para IsOwner se não for encontrada em um arquivo separado.
    # Em produção, você deve ter uma implementação robusta de IsOwner.
    class IsOwner(IsAuthenticated):
        def has_object_permission(self, request, view, obj):
            # Verifica se o objeto tem um atributo 'user' e se ele corresponde ao usuário da requisição
            return obj.user == request.user


class ProgressEntryViewSet(viewsets.ModelViewSet):
    serializer_class = ProgressEntrySerializer
    permission_classes = [IsAuthenticated, IsOwner] # Apenas usuários autenticados e donos podem acessar

    def get_queryset(self):
        """
        Retorna apenas as entradas de progresso do usuário autenticado.
        Se o usuário não estiver autenticado, retorna um queryset vazio para evitar erros.
        """
        user = self.request.user
        if not user.is_authenticated:
            # Se o usuário não está autenticado, não há dados de progresso para ele.
            # Retorna um queryset vazio para evitar o TypeError.
            return ProgressEntry.objects.none()

        queryset = ProgressEntry.objects.filter(user=user)

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            parsed_start_date = parse_date(start_date)
            if parsed_start_date:
                queryset = queryset.filter(date__gte=parsed_start_date)
            else:
                # Retorna um erro 400 Bad Request se a data for inválida
                raise ValueError("Formato de data de início inválido.")
        if end_date:
            parsed_end_date = parse_date(end_date)
            if parsed_end_date:
                queryset = queryset.filter(date__lte=parsed_end_date)
            else:
                # Retorna um erro 400 Bad Request se a data for inválida
                raise ValueError("Formato de data de fim inválido.")

        return queryset.order_by('-date')

    def perform_create(self, serializer):
        """
        Associa a entrada de progresso ao usuário autenticado ao criá-la.
        """
        serializer.save(user=self.request.user)

class ProgressStatsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProgressStatsSerializer

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {'detail': 'Autenticação necessária para acessar estatísticas de progresso.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        entries = ProgressEntry.objects.filter(user=user).order_by('-date')

        current_weight = initial_weight = weight_change = bmi = None

        if entries.exists():
            latest_entry = entries.first()
            current_weight = latest_entry.weight
            first_entry = entries.last()
            initial_weight = first_entry.weight

            if first_entry and current_weight is not None and first_entry.weight is not None:
                weight_change = current_weight - first_entry.weight

            user_profile = User.objects.filter(id=user.id).first()
            if user_profile and user_profile.height and current_weight is not None and user_profile.height > 0:
                h = user_profile.height / 100.0
                bmi = round(current_weight / (h ** 2), 2)

        total_workouts = WorkoutLog.objects.filter(workout__user=user).count()
        active_days = WorkoutLog.objects.filter(workout__user=user).values('created_at__date').distinct().count()
        avg_dur = WorkoutLog.objects.filter(workout__user=user).aggregate(Avg('duracao'))
        average_workout_duration = round(avg_dur['duracao__avg'] or 0, 1)
        calories_burned_total = 0
        calories_consumed_total = (
            ConsumedMealLog.objects.filter(user=user).aggregate(Sum('calories_consumed'))['calories_consumed__sum'] or 0
        )

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

        serializer = self.get_serializer(stats)
        return Response(serializer.data)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated]) # Garante que apenas usuários autenticados possam acessar
def export_progress(request):
    user = request.user
    if not user.is_authenticated:
        # Esta verificação é redundante se IsAuthenticated já estiver funcionando,
        # mas é uma boa prática defensiva para evitar o TypeError.
        return Response({'detail': 'Autenticação necessária para exportar progresso.'}, status=status.HTTP_401_UNAUTHORIZED)

    entries = ProgressEntry.objects.filter(user=user).order_by('date')

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