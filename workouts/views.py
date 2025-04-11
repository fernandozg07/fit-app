from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
from .models import Workout, WorkoutLog
from .serializers import WorkoutSerializer
from .filters import WorkoutFilter
from ai.trainer import ajustar_treino

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
    objetivo = user.objetivo
    intensidade = 'alta' if objetivo == 'ganho de massa muscular' else 'moderada'

    workout = Workout.objects.create(
        user=user,
        workout_type='musculacao',
        intensity=intensidade,
        duration=timedelta(minutes=45),
        carga=20 if intensidade == 'alta' else 10,
        frequency='3x por semana',
        exercises='Agachamento, Supino, Remada',
        series_reps='3x12',
        focus='fullbody'
    )

    try:
        treino_ajustado = ajustar_treino(workout)
        if isinstance(treino_ajustado, dict):
            workout.intensity = treino_ajustado.get('intensity', workout.intensity)
            workout.carga = treino_ajustado.get('carga', workout.carga)
            workout.series_reps = treino_ajustado.get('series_reps', workout.series_reps)
            workout.save()
    except Exception as e:
        print("Erro ao gerar treino com IA:", str(e))

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
