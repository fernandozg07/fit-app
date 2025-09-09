from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Workout
from ai.trainer import ajustar_treino  # Importando a IA

class WorkoutView(APIView):
    def get(self, request):
        user = request.user
        historico = Workout.objects.filter(user=user).values("carga", "reps")

        # Aplicando a IA para ajustar o treino
        novo_treino = ajustar_treino(list(historico))

        return Response({"treino_sugerido": novo_treino})
