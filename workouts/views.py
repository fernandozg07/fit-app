# workouts/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
from .models import Workout, WorkoutLog 
from .serializers import WorkoutSerializer, WorkoutGenerateInputSerializer 
from .filters import WorkoutFilter
from ai.trainer import ajustar_treino # Esta função é para ajustar treinos existentes, não para geração inicial
import json # IMPORTANTE: Importar a biblioteca json

class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = WorkoutFilter

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='feedback')
    def feedback(self, request, pk=None):
        workout = self.get_object()
        nota = int(request.data.get('nota', 3))

        try:
            treino_ajustado = ajustar_treino(workout, nota) 
            if isinstance(treino_ajustado, dict):
                workout.intensity = treino_ajustado.get('intensity', workout.intensity)
                workout.carga = treino_ajustado.get('carga', workout.carga)
                workout.series_reps = treino_ajustado.get('series_reps', workout.series_reps)
                workout.save()
        except Exception as e:
            print("Erro ao ajustar treino com IA:", str(e))

        WorkoutLog.objects.create(
            workout=workout,
            nota=nota,
            duracao=int(workout.duration.total_seconds() // 60)
        )

        serializer = WorkoutSerializer(workout)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_workout(request):
    user = request.user
    
    serializer = WorkoutGenerateInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    workout_type = serializer.validated_data.get('workout_type')
    difficulty = serializer.validated_data.get('difficulty')
    duration_minutes = serializer.validated_data.get('duration')
    muscle_groups = serializer.validated_data.get('muscle_groups')
    equipment = serializer.validated_data.get('equipment', [])
    focus = serializer.validated_data.get('focus', 'fullbody') 
    intensity = serializer.validated_data.get('intensity', 'moderada') 

    # FIX: Lógica para gerar exercícios como uma LISTA DE DICIONÁRIOS
    generated_exercises_list_of_dicts = []
    
    # Exemplo de geração de dados de exercícios estruturados
    # Você pode expandir esta lógica com mais detalhes baseados na IA
    if "pernas" in muscle_groups:
        generated_exercises_list_of_dicts.append({
            "id": 1, 
            "name": "Agachamento",
            "sets": 3,
            "reps": 10,
            "weight": 0,
            "duration": 0,
            "rest_time": 60,
            "instructions": "Realize agachamentos com boa forma, mantendo as costas retas."
        })
        generated_exercises_list_of_dicts.append({
            "id": 2,
            "name": "Leg Press",
            "sets": 3,
            "reps": 12,
            "weight": 50,
            "duration": 0,
            "rest_time": 60,
            "instructions": "Empurre a plataforma com os calcanhares, controlando a descida."
        })
    if "peito" in muscle_groups:
        generated_exercises_list_of_dicts.append({
            "id": 3,
            "name": "Supino Reto",
            "sets": 4,
            "reps": 8,
            "weight": 40,
            "duration": 0,
            "rest_time": 90,
            "instructions": "Deite-se no banco, segure a barra e empurre para cima."
        })
        generated_exercises_list_of_dicts.append({
            "id": 4,
            "name": "Flexões",
            "sets": 3,
            "reps": 15,
            "weight": 0,
            "duration": 0,
            "rest_time": 45,
            "instructions": "Mantenha o corpo reto e desça o peito em direção ao chão."
        })
    if "costas" in muscle_groups:
        generated_exercises_list_of_dicts.append({
            "id": 5,
            "name": "Remada Curvada",
            "sets": 3,
            "reps": 10,
            "weight": 30,
            "duration": 0,
            "rest_time": 75,
            "instructions": "Incline o tronco e puxe a barra em direção ao abdômen."
        })
        generated_exercises_list_of_dicts.append({
            "id": 6,
            "name": "Puxada Alta",
            "sets": 3,
            "reps": 12,
            "weight": 35,
            "duration": 0,
            "rest_time": 60,
            "instructions": "Puxe a barra em direção ao peito, contraindo as costas."
        })
    # Adicione mais lógica para outros grupos musculares e equipamentos, se necessário
    
    if not generated_exercises_list_of_dicts:
        generated_exercises_list_of_dicts.append({
            "id": 0,
            "name": "Exercícios Variados",
            "sets": 3,
            "reps": 10,
            "weight": 0,
            "duration": 0,
            "rest_time": 60,
            "instructions": "Uma série de exercícios para o corpo todo, adaptados ao seu nível."
        }) # Fallback

    # FIX: Converter a lista de dicionários para uma STRING JSON antes de salvar
    exercises_json_str = json.dumps(generated_exercises_list_of_dicts)

    # Cria o objeto Workout com dados dinâmicos
    workout = Workout.objects.create(
        user=user,
        workout_type=workout_type,
        intensity=intensity, 
        duration=timedelta(minutes=duration_minutes),
        carga=20, # Placeholder, pode ser baseado na dificuldade ou histórico do usuário
        frequency='3x por semana', # Placeholder, pode ser dinâmico
        exercises=exercises_json_str, # FIX: Salva como string JSON
        series_reps='3x12', # Placeholder, pode ser dinâmico
        focus=focus 
    )

    return Response({
        'detail': 'Treino criado com sucesso!',
        'workout': WorkoutSerializer(workout).data
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_workout(request):
    data = request.data.copy()
    serializer = WorkoutSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({'detail': 'Treino registrado com sucesso!', 'workout': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_workout_feedback(request, workout_id):
    try:
        workout = Workout.objects.get(id=workout_id, user=request.user)
    except Workout.DoesNotExist:
        return Response({'detail': 'Treino não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    nota = request.data.get('nota')
    duracao = request.data.get('duracao')

    if nota is None or duracao is None:
        return Response({'detail': 'Nota e duração são obrigatórias.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        nota = int(nota)
        duracao = int(duracao)
    except ValueError:
        return Response({'detail': 'Nota e duração devem ser números inteiros.'}, status=status.HTTP_400_BAD_REQUEST)

    if nota < 1 or nota > 5:
        return Response({'detail': 'A nota deve estar entre 1 e 5.'}, status=status.HTTP_400_BAD_REQUEST)

    WorkoutLog.objects.create(workout=workout, nota=nota, duracao=duracao)

    return Response({'detail': 'Feedback registrado com sucesso!'}, status=status.HTTP_201_CREATED)
