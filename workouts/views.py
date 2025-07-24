from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
from .models import Workout, WorkoutLog 
from .serializers import WorkoutSerializer, WorkoutGenerateInputSerializer 
from .filters import WorkoutFilter
from ai.trainer import ajustar_treino_por_feedback # FIX: Importado a função de ajuste por feedback
import json # IMPORTANTE: Importar a biblioteca json
from openai import OpenAI # <--- ADICIONE ESTA LINHA: Importar OpenAI
from decouple import config # <--- ADICIONE ESTA LINHA: Importar config para API Key

# Cliente OpenAI para OpenRouter (certifique-se de que sua chave API está configurada no .env)
client = OpenAI( # <--- ADICIONE ESTE BLOCO
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
    focus = serializer.validated_data.get('focus', 'fullbody') 
    intensity = serializer.validated_data.get('intensity', 'moderada') 

    # <--- INÍCIO DA GRANDE ALTERAÇÃO AQUI: Lógica para gerar exercícios com IA
    # Construir o prompt para a IA
    prompt_parts = [
        f"Gere um treino de {workout_type} com duração de {duration_minutes} minutos para um nível {difficulty}.",
        f"Foque nos grupos musculares: {', '.join(muscle_groups) if muscle_groups else 'corpo todo'}."
    ]
    if equipment:
        prompt_parts.append(f"Utilize os seguintes equipamentos: {', '.join(equipment)}.")
    prompt_parts.append("Retorne uma lista de exercícios em formato JSON, onde cada exercício deve ter 'name', 'sets', 'reps' (como string, ex: '8-12' ou 'até a falha'), 'weight' (como string, ex: '20kg' ou 'peso corporal'), 'duration' (como string, ex: '30s' ou '0' se baseado em repetições), 'rest_time' (como string, ex: '60s'), e 'instructions'.")
    prompt = " ".join(prompt_parts)

    # Definir o schema de resposta esperado
    response_schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "name": { "type": "STRING", "description": "Nome do exercício, ex: Agachamento Livre" },
                "sets": { "type": "NUMBER", "description": "Número de séries, ex: 3" },
                "reps": { "type": "STRING", "description": "Número de repetições ou descrição, ex: '8-12' ou 'até a falha'" },
                "weight": { "type": "STRING", "description": "Peso em kg ou 'peso corporal', ex: '20kg' ou 'peso corporal'" },
                "duration": { "type": "STRING", "description": "Duração em segundos para exercícios baseados em tempo, ex: '30s'. Use '0' se for baseado em repetições." },
                "rest_time": { "type": "STRING", "description": "Tempo de descanso entre as séries em segundos, ex: '60s'" },
                "instructions": { "type": "STRING", "description": "Instruções detalhadas para o exercício." }
            },
            "required": ["name", "sets", "reps", "weight", "duration", "rest_time", "instructions"]
        }
    }

    generated_exercises_list_of_dicts = []
    try:
        # Chamar a IA para gerar os exercícios com o schema definido
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Ou outro modelo que suporte response_schema
            messages=[
                {"role": "system", "content": "Você é um treinador fitness que gera treinos detalhados em formato JSON."},
                {"role": "user", "content": prompt}
            ],
            response_model=response_schema # Usar response_model para garantir o formato
        )
        # A resposta já virá no formato Python (lista de dicionários) devido ao response_model
        generated_exercises_list_of_dicts = response # A resposta já é a lista de exercícios
        
    except Exception as e:
        print(f"Erro ao gerar exercícios com IA: {str(e)}")
        # Fallback para um exercício genérico em caso de falha da IA
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
    # <--- FIM DA GRANDE ALTERAÇÃO AQUI

    # FIX: Converter a lista de dicionários para uma STRING JSON antes de salvar
    exercises_json_str = json.dumps(generated_exercises_list_of_dicts)

    workout = Workout.objects.create(
        user=user,
        workout_type=workout_type,
        intensity=intensity, 
        duration=timedelta(minutes=duration_minutes),
        carga=20, # Placeholder, pode ser baseado na dificuldade ou histórico do usuário
        frequency='3x por semana', # Placeholder, pode ser dinâmico
        exercises=exercises_json_str, # Salva como string JSON
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
