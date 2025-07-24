from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
from .models import Workout, WorkoutLog 
from .serializers import WorkoutSerializer, WorkoutGenerateInputSerializer 
from .filters import WorkoutFilter
from ai.trainer import ajustar_treino_por_feedback
import json
from openai import OpenAI
from decouple import config

# Cliente OpenAI para OpenRouter (certifique-se de que sua chave API está configurada no .env)
client = OpenAI(
    api_key=config("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

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
        duracao_log = int(request.data.get('duracao', 0)) 

        WorkoutLog.objects.create(
            workout=workout,
            nota=nota,
            duracao=duracao_log
        )

        try:
            workout_data_for_ai = {
                'carga': workout.carga,
                'intensity': workout.intensity,
                'series_reps': workout.series_reps
            }
            treino_ajustado = ajustar_treino_por_feedback(workout_data_for_ai, nota)
            
            workout.intensity = treino_ajustado.get('intensity', workout.intensity)
            workout.carga = treino_ajustado.get('carga', workout.carga)
            workout.series_reps = treino_ajustado.get('series_reps', workout.series_reps)
            workout.save()
        except Exception as e:
            print(f"Erro ao ajustar treino com IA no feedback: {str(e)}")

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
    # Removido o valor padrão 'fullbody' aqui, será definido dinamicamente abaixo
    # focus = serializer.validated_data.get('focus', 'fullbody') 
    intensity = serializer.validated_data.get('intensity', 'moderada') 

    # <--- ALTERAÇÃO AQUI: Determinar o valor do 'focus' dinamicamente
    if muscle_groups and len(muscle_groups) > 0:
        # Se grupos musculares específicos forem fornecidos, o foco é a junção deles
        focus_to_save = ', '.join(muscle_groups)
    else:
        # Caso contrário, o foco é 'fullbody' (corpo todo)
        focus_to_save = 'fullbody' 

    # Construir o prompt para a IA (já estava usando muscle_groups, o que é correto)
    prompt_parts = [
        f"Gere um treino de {workout_type} com duração de {duration_minutes} minutos para um nível {difficulty}.",
        f"Foque nos grupos musculares: {focus_to_save if muscle_groups else 'corpo todo'}." # Use focus_to_save para o prompt também para consistência
    ]
    if equipment:
        prompt_parts.append(f"Utilize os seguintes equipamentos: {', '.join(equipment)}.")
    prompt_parts.append("Retorne APENAS uma lista de exercícios em formato JSON. Cada exercício deve ser um objeto com as chaves 'name', 'sets' (número), 'reps' (string, ex: '8-12' ou 'até a falha'), 'weight' (string, ex: '20kg' ou 'peso corporal'), 'duration' (string, ex: '30s' ou '0' se baseado em repetições), 'rest_time' (string, ex: '60s'), e 'instructions'.")
    prompt_parts.append("Não inclua nenhum texto adicional antes ou depois do JSON.")
    prompt = " ".join(prompt_parts)

    generated_exercises_list_of_dicts = []
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "Você é um treinador fitness que gera treinos detalhados em formato JSON. Responda APENAS com o JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000 
        )
        
        ai_response_content = response.choices[0].message.content.strip()
        print(f"Resposta bruta da IA: {ai_response_content}") 

        generated_exercises_list_of_dicts = json.loads(ai_response_content)
        
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da IA: {e}")
        print(f"Conteúdo que causou o erro: {ai_response_content}")
        generated_exercises_list_of_dicts.append({
            "id": 0,
            "name": "Exercícios Variados (Erro de Formato da IA)",
            "sets": 3,
            "reps": "10-12",
            "weight": "0",
            "duration": "0",
            "rest_time": "60s",
            "instructions": "A IA não conseguiu gerar exercícios no formato correto. Por favor, tente novamente ou verifique a configuração da API."
        })
    except Exception as e:
        print(f"Erro inesperado ao gerar exercícios com IA: {str(e)}")
        generated_exercises_list_of_dicts.append({
            "id": 0,
            "name": "Exercícios Variados (Erro na Geração)",
            "sets": 3,
            "reps": "10-12",
            "weight": "0",
            "duration": "0",
            "rest_time": "60s",
            "instructions": "Não foi possível gerar exercícios detalhados no momento. Por favor, tente novamente."
        })

    exercises_json_str = json.dumps(generated_exercises_list_of_dicts)

    workout = Workout.objects.create(
        user=user,
        workout_type=workout_type,
        intensity=intensity, 
        duration=timedelta(minutes=duration_minutes),
        carga=20, 
        frequency='3x por semana', 
        exercises=exercises_json_str, 
        series_reps='3x12', 
        focus=focus_to_save, # <--- Use a variável 'focus_to_save' aqui
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
