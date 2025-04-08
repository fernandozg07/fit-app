from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
from .models import Workout, WorkoutLog
from .serializers import WorkoutSerializer, WorkoutLogSerializer
from ai.trainer import ajustar_treino


class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='feedback')
    def feedback(self, request, pk=None):
        """
        Endpoint alternativo para enviar feedback e ajustar treino (simples).
        """
        workout = self.get_object()
        nota = int(request.data.get('nota', 3))
        treino_ajustado = ajustar_treino(workout, nota)
        serializer = WorkoutSerializer(treino_ajustado)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_workout(request):
    """
    Gera um treino automático baseado no objetivo do usuário e ajusta com IA.
    """
    user = request.user
    objetivo = user.objetivo
    intensidade = 'alta' if objetivo == 'ganho de massa muscular' else 'moderada'

    workout = Workout.objects.create(
        user=user,
        name=f"Treino para {objetivo}",
        description=f"Treino gerado automaticamente com intensidade {intensidade}.",
        duration=45,
        intensity=intensidade,
        carga=20 if intensidade == 'alta' else 10,
        date=datetime.now().date()
    )

    historico = Workout.objects.filter(user=user).order_by('-date')[:5]

    try:
        treino_ajustado = ajustar_treino(historico)
        if treino_ajustado:
            workout.intensity = treino_ajustado.get('intensity', workout.intensity)
            workout.carga = treino_ajustado.get('carga', workout.carga)
            workout.save()
            return Response({
                'detail': 'Treino criado e ajustado com sucesso!',
                'workout': WorkoutSerializer(workout).data
            }, status=status.HTTP_201_CREATED)
    except Exception as e:
        print("Erro na IA:", str(e))

    return Response({
        'detail': 'Treino criado com sucesso, mas não foi possível ajustar com IA.',
        'workout': WorkoutSerializer(workout).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_workout(request):
    """
    Registra um treino manualmente.
    """
    data = request.data.copy()
    data['user'] = request.user.id
    serializer = WorkoutSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response({'detail': 'Treino registrado com sucesso!', 'workout': serializer.data}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_workout_feedback(request, workout_id):
    """
    Registra feedback de um treino após a execução.
    """
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
