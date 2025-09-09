# workouts/views.py
import datetime
import random
from types import SimpleNamespace
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
from .models import Workout, WorkoutLog, WorkoutFeedback, FOCUS_CHOICES, WORKOUT_TYPES, INTENSITY_LEVELS, DIFFICULTY_CHOICES 
from .serializers import WorkoutSerializer, WorkoutGenerateInputSerializer, WorkoutFeedbackSerializer
from .filters import WorkoutFilter
from ai.trainer import ajustar_treino_por_feedback # Certifique-se de que este módulo e função existem
import json
from openai import OpenAI
from decouple import config
import re

# Cliente OpenAI para OpenRouter (certifique-se de que sua chave API está configurada no .env)
client = OpenAI(
    api_key=config("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def map_muscle_groups_to_focus(muscle_groups_list):
    """
    Mapeia uma lista de grupos musculares para uma categoria de foco mais ampla
    usando as escolhas definidas em FOCUS_CHOICES.
    """
    lower_body_muscles = ['pernas', 'gluteos', 'panturrilhas', 'quadriceps', 'isquiotibiais']
    upper_body_muscles = ['peito', 'costas', 'ombros', 'biceps', 'triceps', 'antebraco', 'braços']
    core_muscles = ['abdomen', 'core', 'oblíquos']

    muscle_groups_lower = [m.lower() for m in muscle_groups_list]

    has_lower = any(m in lower_body_muscles for m in muscle_groups_lower)
    has_upper = any(m in upper_body_muscles for m in muscle_groups_lower)
    has_core = any(m in core_muscles for m in muscle_groups_lower)

    if not muscle_groups_list:
        return 'fullbody' 
    elif has_lower and not has_upper and not has_core:
        return 'lower_body'
    elif has_upper and not has_lower and not has_core:
        return 'upper_body'
    elif has_core and not has_lower and not has_upper:
        return 'core'
    elif has_lower and has_upper: 
        return 'fullbody' 
    else:
        focus_choices_keys = [choice[0] for choice in FOCUS_CHOICES]
        if 'custom' in focus_choices_keys:
            return 'custom'
        return 'fullbody'


class WorkoutViewSet(viewsets.ModelViewSet):
    """
    Viewset para operações CRUD em Treinos.
    """
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = WorkoutFilter

    def perform_create(self, serializer):
        """
        Associa o usuário autenticado ao treino ao criá-lo.
        """
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
        Retorna apenas os treinos do usuário autenticado, ordenados por data de criação.
        """
        user = self.request.user
        if user.is_authenticated:
            return Workout.objects.filter(user=user).order_by('-created_at') 
        else:
            return Workout.objects.none()

    @action(detail=True, methods=['post'], url_path='feedback')
    def feedback(self, request, pk=None):
        """
        Endpoint para registrar feedback sobre um treino específico.
        Cria um WorkoutFeedback e um WorkoutLog (para duração e detalhes por exercício).
        """
        workout = self.get_object()
        
        serializer = WorkoutFeedbackSerializer(data=request.data, context={'request': request, 'workout': workout})
        serializer.is_valid(raise_exception=True)

        rating = serializer.validated_data.get('rating')
        comments = serializer.validated_data.get('comments', '') 
        duration_minutes = serializer.validated_data.get('duration_minutes', 0) 
        exercise_logs = serializer.validated_data.get('exercise_logs', []) 

        # Cria o log de treino (para duração, nota e DETALHES POR EXERCÍCIO)
        workout_log = WorkoutLog.objects.create(
            workout=workout,
            nota=rating,
            duracao=duration_minutes,
            exercise_logs=exercise_logs 
        )
        
        # Cria o feedback detalhado
        WorkoutFeedback.objects.create(
            user=request.user,
            workout=workout,
            workout_log=workout_log,
            rating=rating,
            comments=comments 
        )

        try:
            workout_data_for_ai = {
                'carga': workout.carga,
                'intensity': workout.intensity,
                'series_reps': workout.series_reps
            }
            treino_ajustado = ajustar_treino_por_feedback(workout_data_for_ai, rating)
            
            workout.intensity = treino_ajustado.get('intensity', workout.intensity)
            workout.carga = treino_ajustado.get('carga', workout.carga)
            workout.series_reps = treino_ajustado.get('series_reps', workout.series_reps)
            workout.save()
        except Exception as e:
            print(f"Erro ao ajustar treino com IA no feedback: {str(e)}")

        serializer = WorkoutSerializer(workout)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_workout(request):
    """
    Gera um treino personalizado usando IA com base nos parâmetros fornecidos.
    """
    user = request.user
    
    serializer = WorkoutGenerateInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    workout_type = serializer.validated_data.get('workout_type')
    difficulty = serializer.validated_data.get('difficulty')
    duration_minutes = serializer.validated_data.get('duration') # Duração em minutos do input do usuário
    muscle_groups = serializer.validated_data.get('muscle_groups')
    equipment = serializer.validated_data.get('equipment', [])
    intensity = serializer.validated_data.get('intensity', 'moderada') 

    if duration_minutes <= 20:
        num_exercises = random.randint(2, 4)
    elif duration_minutes <= 40:
        num_exercises = random.randint(4, 7)
    elif duration_minutes <= 60:
        num_exercises = random.randint(7, 10)
    else: 
        num_exercises = random.randint(10, 15)

    prompt_parts = [
        f"Gere um treino de {workout_type} com duração de {duration_minutes} minutos para um nível {difficulty}.",
        f"O treino deve conter aproximadamente {num_exercises} exercícios.",
        f"Foque nos grupos musculares: {', '.join(muscle_groups) if muscle_groups else 'corpo inteiro'}."
    ]
    if equipment:
        prompt_parts.append(f"Utilize os seguintes equipamentos: {', '.join(equipment)}.")
    
    prompt_parts.append("Retorne APENAS um objeto JSON principal. Este objeto deve conter duas chaves: 'workout_details' e 'exercises'.")
    prompt_parts.append("A chave 'workout_details' deve ser um objeto com as chaves 'workout_name' (string, nome criativo do treino), 'workout_description' (string, descrição geral do treino), 'series_reps_overall' (string, ex: '3 séries de 10-12 repetições'), 'frequency_overall' (string, ex: '3x por semana'), 'carga_overall' (string, ex: 'moderada' ou '50kg').")
    prompt_parts.append("A chave 'exercises' deve ser uma lista de objetos. Cada objeto de exercício deve ter as chaves 'id' (número), 'name' (string, nome do exercício), 'sets' (string, ex: '3'), 'reps' (string, ex: '8-12' ou 'até a falha'), 'weight' (string, ex: '20kg' ou 'peso corporal'), 'duration' (string, ex: '30s' ou '0' se baseado em repetições), 'rest_time' (string, ex: '60s'), e 'instructions' (string, como executar o exercício).")
    prompt_parts.append("Certifique-se de que o JSON é válido e não contém texto adicional antes ou depois.")
    prompt = " ".join(prompt_parts)

    generated_exercises_list_of_dicts = []
    workout_name_fallback = f"{workout_type.capitalize()} - {difficulty.capitalize()} ({duration_minutes}min)" 
    workout_description_fallback = f"Este treino de {workout_type} de {duration_minutes} minutos é projetado para o nível {difficulty}, focando em {', '.join(muscle_groups) if muscle_groups else 'corpo inteiro'}."
    series_reps_overall_fallback = '3x12'
    frequency_overall_fallback = '3x por semana'
    carga_overall_fallback = 'Peso Corporal' 

    ai_response_content = ""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "Você é um treinador fitness que gera treinos detalhados em formato JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500, 
            temperature=0.7
        )
        
        ai_response_content = response.choices[0].message.content.strip()
        print(f"DEBUG - Resposta bruta da IA para treino: {ai_response_content}")

        match = re.search(r'\{.*\}', ai_response_content, re.DOTALL)
        if match:
            json_string = match.group(0)
            ai_generated_data = json.loads(json_string)

            generated_exercises_list_of_dicts = ai_generated_data.get('exercises', [])
            workout_details = ai_generated_data.get('workout_details', {})

            workout_name = workout_details.get('workout_name', workout_name_fallback)
            workout_description = workout_details.get('workout_description', workout_description_fallback)
            series_reps_overall = workout_details.get('series_reps_overall', series_reps_overall_fallback)
            frequency_overall = workout_details.get('frequency_overall', frequency_overall_fallback)
            carga_overall = workout_details.get('carga_overall', carga_overall_fallback)

        else:
            raise json.JSONDecodeError("JSON principal não encontrado na resposta da IA", ai_response_content, 0)
        
        for i, exercise in enumerate(generated_exercises_list_of_dicts):
            if 'id' not in exercise:
                exercise['id'] = i + 1

    except json.JSONDecodeError as e:
        print(f"ERRO - Falha ao decodificar JSON da IA para treino: {e}")
        print(f"ERRO - Conteúdo que causou o erro: {ai_response_content}")
        generated_exercises_list_of_dicts = [{
            "id": 1,
            "name": "Exercícios Padrão (Erro de Geração IA)",
            "sets": "3",
            "reps": "10-12",
            "weight": "Peso Corporal",
            "duration": "0",
            "rest_time": "60s",
            "instructions": "Não foi possível gerar exercícios detalhados no momento. Por favor, tente novamente ou verifique a configuração da API. Este é um treino de fallback."
        }]
        workout_name = workout_name_fallback
        workout_description = workout_description_fallback
        series_reps_overall = series_reps_overall_fallback
        frequency_overall = frequency_overall_fallback
        carga_overall = carga_overall_fallback
    except Exception as e:
        print(f"ERRO - Inesperado ao gerar exercícios com IA: {str(e)}")
        generated_exercises_list_of_dicts = [{
            "id": 1,
            "name": "Exercícios Padrão (Erro Inesperado)",
            "sets": "3",
            "reps": "10-12",
            "weight": "Peso Corporal",
            "duration": "0",
            "rest_time": "60s",
            "instructions": "Ocorreu um erro inesperado ao gerar o treino. Tente novamente mais tarde. Este é um treino de fallback."
        }]
        workout_name = workout_name_fallback
        workout_description = workout_description_fallback
        series_reps_overall = series_reps_overall_fallback
        frequency_overall = frequency_overall_fallback
        carga_overall = carga_overall_fallback

    exercises_json_str = json.dumps(generated_exercises_list_of_dicts)

    workout_focus = map_muscle_groups_to_focus(muscle_groups)
    
    try:
        carga_overall_int = int(carga_overall)
    except (ValueError, TypeError):
        carga_overall_int = 0

    workout = Workout.objects.create(
        user=user,
        workout_type=workout_type,
        intensity=intensity, 
        duration=timedelta(minutes=duration_minutes), # Usando duration_minutes diretamente aqui
        carga=carga_overall_int, 
        frequency=frequency_overall, 
        exercises=exercises_json_str, 
        series_reps=series_reps_overall, 
        focus=workout_focus, 
        
        name=workout_name,
        description=workout_description,
        difficulty=difficulty,
        muscle_groups=muscle_groups, 
        equipment=equipment, 
        rating=None,
        completed_date=None,
        status='pending',
    )

    return Response({
        'detail': 'Treino criado com sucesso!',
        'workout': WorkoutSerializer(workout).data 
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_workout(request):
    """
    Registra um treino existente no banco de dados.
    """
    data = request.data.copy()
    serializer = WorkoutSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({'detail': 'Treino registrado com sucesso!', 'workout': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)