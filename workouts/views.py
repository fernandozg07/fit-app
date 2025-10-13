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
from decouple import config
import re

# Base de dados de exercícios para geração local
EXERCISE_DATABASE = {
    'musculacao': {
        'upper_body': {
            'iniciante': [
                {"name": "Flexão de Braço (Joelhos)", "sets": "3", "reps": "8-12", "weight": "Peso Corporal", "instructions": "Apoie os joelhos no chão, mantenha o corpo reto"},
                {"name": "Rosca Direta com Garrafa", "sets": "3", "reps": "12-15", "weight": "1-2kg", "instructions": "Use garrafas de água como peso, contraia o bíceps"},
                {"name": "Tríceps na Cadeira", "sets": "3", "reps": "8-12", "weight": "Peso Corporal", "instructions": "Apoie as mãos na cadeira, desça o corpo"},
                {"name": "Elevação Lateral com Garrafas", "sets": "3", "reps": "10-15", "weight": "1-2kg", "instructions": "Eleve os braços lateralmente até a altura dos ombros"}
            ],
            'intermediario': [
                {"name": "Flexão de Braço", "sets": "3", "reps": "12-20", "weight": "Peso Corporal", "instructions": "Mantenha o corpo reto, desça até o peito quase tocar o chão"},
                {"name": "Rosca Direta com Halteres", "sets": "3", "reps": "12-15", "weight": "5-10kg", "instructions": "Mantenha os cotovelos fixos, contraia o bíceps"},
                {"name": "Tríceps Testa", "sets": "3", "reps": "10-12", "weight": "5-8kg", "instructions": "Deite-se, mantenha os cotovelos fixos"},
                {"name": "Desenvolvimento com Halteres", "sets": "3", "reps": "10-15", "weight": "8-12kg", "instructions": "Empurre os halteres para cima, controle a descida"}
            ],
            'avancado': [
                {"name": "Flexão Diamante", "sets": "4", "reps": "8-15", "weight": "Peso Corporal", "instructions": "Forme um diamante com as mãos, foque no tríceps"},
                {"name": "Rosca Martelo", "sets": "4", "reps": "10-12", "weight": "12-20kg", "instructions": "Mantenha os punhos neutros, alterne os braços"},
                {"name": "Supino com Halteres", "sets": "4", "reps": "8-12", "weight": "15-25kg", "instructions": "Deite-se, empurre os halteres para cima"},
                {"name": "Remada Curvada", "sets": "4", "reps": "10-12", "weight": "15-25kg", "instructions": "Curve o tronco, puxe os halteres em direção ao abdômen"}
            ]
        },
        'lower_body': {
            'iniciante': [
                {"name": "Agachamento Assistido", "sets": "3", "reps": "10-15", "weight": "Peso Corporal", "instructions": "Use uma cadeira como apoio, desça devagar"},
                {"name": "Elevação de Panturrilha", "sets": "3", "reps": "15-20", "weight": "Peso Corporal", "instructions": "Suba na ponta dos pés, contraia as panturrilhas"},
                {"name": "Ponte de Glúteo", "sets": "3", "reps": "12-15", "weight": "Peso Corporal", "instructions": "Deite-se, eleve o quadril contraindo o glúteo"}
            ],
            'intermediario': [
                {"name": "Agachamento", "sets": "3", "reps": "15-20", "weight": "Peso Corporal", "instructions": "Desça até as coxas ficarem paralelas ao chão"},
                {"name": "Afundo", "sets": "3", "reps": "12 cada perna", "weight": "Peso Corporal", "instructions": "Dê um passo à frente, desça o joelho traseiro"},
                {"name": "Agachamento Búlgaro", "sets": "3", "reps": "10 cada perna", "weight": "Peso Corporal", "instructions": "Apoie um pé atrás, agache com a perna da frente"}
            ],
            'avancado': [
                {"name": "Agachamento com Salto", "sets": "4", "reps": "12-15", "weight": "Peso Corporal", "instructions": "Agache e salte explosivamente"},
                {"name": "Pistol Squat Assistido", "sets": "4", "reps": "5-8 cada perna", "weight": "Peso Corporal", "instructions": "Agachamento em uma perna só, use apoio se necessário"},
                {"name": "Afundo com Salto", "sets": "4", "reps": "10 cada perna", "weight": "Peso Corporal", "instructions": "Alterne as pernas saltando"}
            ]
        },
        'fullbody': {
            'iniciante': [
                {"name": "Flexão de Braço (Joelhos)", "sets": "3", "reps": "8-12", "weight": "Peso Corporal", "instructions": "Apoie os joelhos, trabalhe peito e braços"},
                {"name": "Agachamento", "sets": "3", "reps": "10-15", "weight": "Peso Corporal", "instructions": "Trabalha pernas e glúteos"},
                {"name": "Prancha", "sets": "3", "reps": "0", "weight": "Peso Corporal", "duration": "20-30s", "instructions": "Mantenha o corpo reto, fortaleça o core"}
            ],
            'intermediario': [
                {"name": "Burpee", "sets": "3", "reps": "8-12", "weight": "Peso Corporal", "instructions": "Exercício completo: agachamento, prancha, salto"},
                {"name": "Mountain Climber", "sets": "3", "reps": "20", "weight": "Peso Corporal", "instructions": "Posição de prancha, alterne os joelhos ao peito"},
                {"name": "Thruster com Halteres", "sets": "3", "reps": "10-12", "weight": "5-10kg", "instructions": "Agachamento + desenvolvimento em um movimento"}
            ],
            'avancado': [
                {"name": "Burpee com Flexão", "sets": "4", "reps": "10-15", "weight": "Peso Corporal", "instructions": "Burpee completo com flexão na descida"},
                {"name": "Turkish Get-Up", "sets": "3", "reps": "5 cada lado", "weight": "8-15kg", "instructions": "Movimento complexo do chão até em pé"},
                {"name": "Man Maker", "sets": "3", "reps": "8-10", "weight": "8-12kg", "instructions": "Flexão + remada + thruster em sequência"}
            ]
        }
    },
    'cardio': {
        'geral': {
            'iniciante': [
                {"name": "Caminhada no Lugar", "sets": "3", "reps": "0", "weight": "Peso Corporal", "duration": "2min", "instructions": "Mantenha um ritmo confortável"},
                {"name": "Marcha Estacionária", "sets": "3", "reps": "30", "weight": "Peso Corporal", "instructions": "Eleve os joelhos alternadamente"}
            ],
            'intermediario': [
                {"name": "Jumping Jacks", "sets": "4", "reps": "20", "weight": "Peso Corporal", "instructions": "Pule abrindo e fechando pernas e braços"},
                {"name": "High Knees", "sets": "4", "reps": "30", "weight": "Peso Corporal", "instructions": "Corrida no lugar elevando bem os joelhos"}
            ],
            'avancado': [
                {"name": "Burpee", "sets": "5", "reps": "15", "weight": "Peso Corporal", "instructions": "Movimento explosivo completo"},
                {"name": "Sprint no Lugar", "sets": "5", "reps": "0", "weight": "Peso Corporal", "duration": "30s", "instructions": "Corrida intensa no lugar"}
            ]
        }
    },
    'hiit': {
        'geral': {
            'iniciante': [
                {"name": "Agachamento", "sets": "4", "reps": "15", "weight": "Peso Corporal", "instructions": "30s trabalho, 30s descanso"},
                {"name": "Flexão (Joelhos)", "sets": "4", "reps": "10", "weight": "Peso Corporal", "instructions": "30s trabalho, 30s descanso"}
            ],
            'intermediario': [
                {"name": "Burpee", "sets": "6", "reps": "10", "weight": "Peso Corporal", "instructions": "45s trabalho, 15s descanso"},
                {"name": "Mountain Climber", "sets": "6", "reps": "20", "weight": "Peso Corporal", "instructions": "45s trabalho, 15s descanso"}
            ],
            'avancado': [
                {"name": "Burpee com Salto", "sets": "8", "reps": "12", "weight": "Peso Corporal", "instructions": "50s trabalho, 10s descanso"},
                {"name": "Thruster", "sets": "8", "reps": "15", "weight": "10-15kg", "instructions": "50s trabalho, 10s descanso"}
            ]
        }
    }
}

def generate_local_exercises(workout_type, muscle_groups, equipment, difficulty, duration_minutes, num_exercises):
    """Gera exercícios localmente baseado nos parâmetros"""
    
    # Determina o foco baseado nos grupos musculares
    focus = 'fullbody'
    if muscle_groups:
        lower_body_muscles = ['pernas', 'gluteos', 'panturrilhas', 'quadriceps', 'isquiotibiais']
        upper_body_muscles = ['peito', 'costas', 'ombros', 'biceps', 'triceps', 'antebraco', 'braços']
        
        muscle_groups_lower = [m.lower() for m in muscle_groups]
        has_lower = any(m in lower_body_muscles for m in muscle_groups_lower)
        has_upper = any(m in upper_body_muscles for m in muscle_groups_lower)
        
        if has_lower and not has_upper:
            focus = 'lower_body'
        elif has_upper and not has_lower:
            focus = 'upper_body'
    
    # Seleciona exercícios da base de dados
    exercises_pool = []
    
    if workout_type in EXERCISE_DATABASE:
        if focus in EXERCISE_DATABASE[workout_type]:
            if difficulty in EXERCISE_DATABASE[workout_type][focus]:
                exercises_pool = EXERCISE_DATABASE[workout_type][focus][difficulty]
        elif 'geral' in EXERCISE_DATABASE[workout_type]:
            if difficulty in EXERCISE_DATABASE[workout_type]['geral']:
                exercises_pool = EXERCISE_DATABASE[workout_type]['geral'][difficulty]
    
    # Se não encontrou exercícios, usa exercícios básicos
    if not exercises_pool:
        exercises_pool = [
            {"name": "Exercício Básico", "sets": "3", "reps": "10-12", "weight": "Peso Corporal", "instructions": "Exercício adaptado ao seu nível"}
        ]
    
    # Seleciona exercícios aleatórios até atingir o número desejado
    selected_exercises = []
    available_exercises = exercises_pool.copy()
    
    for i in range(min(num_exercises, len(available_exercises) * 2)):  # Permite repetição se necessário
        if not available_exercises:
            available_exercises = exercises_pool.copy()
        
        exercise = available_exercises.pop(random.randint(0, len(available_exercises) - 1))
        exercise_copy = exercise.copy()
        exercise_copy['id'] = i + 1
        exercise_copy['rest_time'] = '60s' if 'rest_time' not in exercise_copy else exercise_copy['rest_time']
        exercise_copy['duration'] = '0' if 'duration' not in exercise_copy else exercise_copy['duration']
        
        selected_exercises.append(exercise_copy)
        
        if len(selected_exercises) >= num_exercises:
            break
    
    return selected_exercises

# Sistema de geração local (sem dependência externa)
USE_LOCAL_GENERATION = True

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

    # Usa sistema de geração local inteligente
    try:
        generated_exercises_list_of_dicts = generate_local_exercises(
            workout_type, muscle_groups, equipment, difficulty, duration_minutes, num_exercises
        )
        
        workout_name = workout_name_fallback
        workout_description = workout_description_fallback
        series_reps_overall = series_reps_overall_fallback
        frequency_overall = frequency_overall_fallback
        carga_overall = carga_overall_fallback
        
        for i, exercise in enumerate(generated_exercises_list_of_dicts):
            if 'id' not in exercise:
                exercise['id'] = i + 1
    except Exception as e:
        print(f"INFO - Usando geração local de exercícios: {str(e)}")
        # Sistema de geração local inteligente
        generated_exercises_list_of_dicts = generate_local_exercises(
            workout_type, muscle_groups, equipment, difficulty, duration_minutes, num_exercises
        )
        
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