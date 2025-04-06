from datetime import timedelta
from random import randint, choice

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Diet, Workout, DietFeedback
from .serializers import DietSerializer, WorkoutSerializer, DietFeedbackSerializer
from ai.trainer import ajustar_treino


# ViewSet para Dietas
class DietViewSet(viewsets.ModelViewSet):
    serializer_class = DietSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Diet.objects.filter(user=user)

        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(date=date)

        return queryset.order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


# ViewSet para Treinos
class WorkoutViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


# Geração automática de dieta com base no objetivo
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_diet(request):
    user = request.user
    fitness_goal = request.data.get('fitness_goal') or user.fitness_goal

    if not fitness_goal:
        return Response({'detail': 'Objetivo não encontrado na requisição.'}, status=status.HTTP_400_BAD_REQUEST)

    diet_config = {
        'perda de peso': {
            'meals': ['breakfast', 'lunch', 'dinner'],
            'calories': (400, 600),
            'protein': (30, 50),
            'carbs': (40, 60),
            'fat': (10, 20),
        },
        'ganho muscular': {
            'meals': ['lunch', 'dinner'],
            'calories': (700, 900),
            'protein': (60, 80),
            'carbs': (70, 100),
            'fat': (20, 30),
        },
        'flexibilidade': {
            'meals': ['snack'],
            'calories': (200, 300),
            'protein': (10, 20),
            'carbs': (30, 50),
            'fat': (5, 10),
        },
    }

    config = diet_config.get(fitness_goal.lower())
    if not config:
        return Response({'detail': 'Objetivo de dieta inválido.'}, status=status.HTTP_400_BAD_REQUEST)

    diet = Diet.objects.create(
        user=user,
        meal=choice(config['meals']),
        calories=randint(*config['calories']),
        protein=randint(*config['protein']),
        carbs=randint(*config['carbs']),
        fat=randint(*config['fat']),
    )

    return Response(DietSerializer(diet).data, status=status.HTTP_201_CREATED)


# Geração automática de treino com ajuste por IA
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_workout(request):
    user = request.user
    fitness_goal = request.data.get('fitness_goal') or user.fitness_goal

    if not fitness_goal:
        return Response({'detail': 'Objetivo não encontrado na requisição.'}, status=status.HTTP_400_BAD_REQUEST)

    workout_data = {
        'perda de peso': (
            'cardio', 'Alta', timedelta(minutes=45),
            'Corrida, Bicicleta, Pular corda', '', '5 vezes por semana'
        ),
        'ganho muscular': (
            'musculacao', 'Moderada', timedelta(hours=1),
            'Supino, Agachamento, Levantamento terra, Flexões',
            '3 séries de 12 repetições por exercício', '3 vezes por semana'
        ),
        'flexibilidade': (
            'flexibilidade', 'Baixa', timedelta(minutes=30),
            'Alongamentos gerais', '', '3 vezes por semana'
        ),
    }

    config = workout_data.get(fitness_goal.lower())
    if not config:
        return Response({'detail': 'Objetivo de treino inválido.'}, status=status.HTTP_400_BAD_REQUEST)

    workout_type, intensity, duration, exercises, series_reps, frequency = config

    workout = Workout.objects.create(
        user=user,
        workout_type=workout_type,
        intensity=intensity,
        duration=duration,
        exercises=exercises,
        series_reps=series_reps,
        frequency=frequency
    )

    # Ajuste inteligente com IA
    historico = list(Workout.objects.filter(user=user).values("intensity", "series_reps", "carga"))
    for treino in historico:
        treino.setdefault("carga", 0)

    treino_ajustado = ajustar_treino(historico)
    workout.intensity = treino_ajustado.get('intensity', intensity)
    workout.carga = treino_ajustado.get('carga', getattr(workout, 'carga', 0))
    workout.save()

    return Response(WorkoutSerializer(workout).data, status=status.HTTP_201_CREATED)


# Registro manual de treino
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def log_workout(request):
    serializer = WorkoutSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Recebimento de feedback textual (treino ou geral)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def provide_feedback(request):
    feedback = request.data.get('feedback')
    if feedback:
        print(f"Feedback do usuário: {feedback}")
        return Response({"message": "Feedback recebido!"})
    return Response({"detail": "Feedback vazio."}, status=status.HTTP_400_BAD_REQUEST)


# Recebimento de feedback de dieta com salvamento no banco
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def diet_feedback(request):
    serializer = DietFeedbackSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
