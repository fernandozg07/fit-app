from datetime import timedelta

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Workout, WorkoutLog, WorkoutFeedback
from .serializers import WorkoutSerializer
from ai.trainer import ajustar_treino
from diets.models import Diet, DietFeedback


class WorkoutViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


def adjust_workout_based_on_feedback(workout, rating):
    if rating >= 4:
        if 'musculacao' in workout.workout_type:
            workout.intensity = 'Alta'
            workout.duration += timedelta(minutes=15)
            workout.carga += 5
        elif 'cardio' in workout.workout_type:
            workout.intensity = 'Moderada'
            workout.duration += timedelta(minutes=10)
    elif rating <= 2:
        workout.intensity = 'Baixa'
        workout.duration = max(timedelta(minutes=30), workout.duration - timedelta(minutes=10))
        workout.carga = max(5, workout.carga - 5)
    return workout


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_workout(request):
    user = request.user
    fitness_goal = request.data.get('fitness_goal')

    if not fitness_goal:
        return Response({'detail': 'Objetivo não fornecido.'}, status=status.HTTP_400_BAD_REQUEST)

    workout_options = {
        'perda de peso': {
            'workout_type': 'cardio',
            'intensity': 'Alta',
            'duration': timedelta(minutes=45),
            'exercises': 'Corrida, Bicicleta, Pular corda',
            'series_reps': '',
            'frequency': '5 vezes por semana',
            'carga': 10,
        },
        'ganho muscular': {
            'workout_type': 'musculacao',
            'intensity': 'Moderada',
            'duration': timedelta(hours=1),
            'exercises': 'Supino, Agachamento, Levantamento terra, Flexões',
            'series_reps': '3 séries de 12 repetições por exercício',
            'frequency': '3 vezes por semana',
            'carga': 15,
        },
        'flexibilidade': {
            'workout_type': 'flexibilidade',
            'intensity': 'Baixa',
            'duration': timedelta(minutes=30),
            'exercises': 'Alongamentos gerais',
            'series_reps': '',
            'frequency': '3 vezes por semana',
            'carga': 5,
        }
    }

    config = workout_options.get(fitness_goal)
    if not config:
        return Response({'detail': 'Objetivo de fitness inválido.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        workout = Workout.objects.create(user=user, **config)
    except Exception as e:
        return Response({'detail': f'Erro ao criar treino: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    historico = list(Workout.objects.filter(user=user).values("intensity", "series_reps", "carga"))
    for h in historico:
        h.setdefault("carga", 0)

    try:
        treino_ajustado = ajustar_treino(historico)
        workout.intensity = treino_ajustado.get('intensity', workout.intensity)
        workout.carga = treino_ajustado.get('carga', workout.carga)
        workout.save()
    except Exception as e:
        print("Erro na IA:", str(e))
    return Response({
        'detail': 'Treino criado com sucesso, mas não foi possível ajustar com IA.',
        'workout': WorkoutSerializer(workout).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def provide_feedback(request):
    user = request.user
    workout_id = request.data.get('workout_id')
    diet_id = request.data.get('diet_id')
    feedback_text = request.data.get('feedback_text', '')
    rating = request.data.get('rating')

    if rating is None:
        return Response({'detail': 'A avaliação (rating) é obrigatória.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        rating = int(rating)
        if not 1 <= rating <= 5:
            raise ValueError
    except (ValueError, TypeError):
        return Response({'detail': 'A avaliação deve estar entre 1 e 5.'}, status=status.HTTP_400_BAD_REQUEST)

    if workout_id:
        try:
            workout = Workout.objects.get(id=workout_id, user=user)
        except Workout.DoesNotExist:
            return Response({'detail': 'Treino não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        WorkoutFeedback.objects.create(
            user=user,
            workout=workout,
            feedback_text=feedback_text,
            rating=rating
        )

        workout = adjust_workout_based_on_feedback(workout, rating)
        workout.save()

        return Response({'detail': 'Feedback do treino enviado com sucesso!'}, status=status.HTTP_201_CREATED)

    elif diet_id:
        try:
            diet = Diet.objects.get(id=diet_id, user=user)
        except Diet.DoesNotExist:
            return Response({'detail': 'Dieta não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        DietFeedback.objects.create(
            user=user,
            diet=diet,
            feedback_text=feedback_text,
            rating=rating
        )

        return Response({'detail': 'Feedback da dieta enviado com sucesso!'}, status=status.HTTP_201_CREATED)

    return Response({'detail': 'ID do treino ou da dieta é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_workout(request):
    user = request.user
    workout_id = request.data.get('workout_id')
    duration = request.data.get('duration')

    if not workout_id or duration is None:
        return Response({'detail': 'ID do treino e duração são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        duration = float(duration)
        if duration <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return Response({'detail': 'Duração inválida.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        workout = Workout.objects.get(id=workout_id, user=user)
    except Workout.DoesNotExist:
        return Response({'detail': 'Treino não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    WorkoutLog.objects.create(
        user=user,
        workout=workout,
        duration=timedelta(minutes=duration)
    )

    return Response({'detail': 'Treino registrado com sucesso!'}, status=status.HTTP_201_CREATED)
