from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Diet, DietFeedback, Workout
from .serializers import DietSerializer, DietFeedbackSerializer, WorkoutSerializer

# IA simulada de exemplo
def ajustar_treino(workout, feedback_nota):
    if feedback_nota >= 4:
        workout.carga += 2.5
    elif feedback_nota <= 2:
        workout.carga = max(0, workout.carga - 2.5)
    workout.save()
    return workout

class DietViewSet(viewsets.ModelViewSet):
    queryset = Diet.objects.all()
    serializer_class = DietSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Diet.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='feedback')
    def add_feedback(self, request, pk=None):
        diet = self.get_object()
        serializer = DietFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, diet=diet)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        workout = self.get_object()
        nota = int(request.data.get('nota', 3))
        treino_ajustado = ajustar_treino(workout, nota)
        serializer = WorkoutSerializer(treino_ajustado)
        return Response(serializer.data)
