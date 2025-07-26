from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
from .models import Workout, WorkoutLog, WorkoutFeedback # Importar WorkoutFeedback
from .serializers import WorkoutSerializer, WorkoutGenerateInputSerializer, WorkoutFeedbackSerializer # Importar WorkoutFeedbackSerializer
from .filters import WorkoutFilter # Importar WorkoutFilter
from ai.trainer import ajustar_treino_por_feedback # Certifique-se de que este módulo e função existem
import json
from openai import OpenAI
from decouple import config
import re # Importar o módulo 're'

# Cliente OpenAI para OpenRouter (certifique-se de que sua chave API está configurada no .env)
client = OpenAI(
    api_key=config("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

class WorkoutViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD em Treinos.
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
        Retorna apenas os treinos do usuário autenticado.
        """
        return Workout.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='feedback')
    def feedback(self, request, pk=None):
        """
        Endpoint para registrar feedback sobre um treino específico.
        Cria um WorkoutFeedback e um WorkoutLog (para duração).
        """
        workout = self.get_object()
        
        # Dados do feedback
        rating = request.data.get('rating')
        comments = request.data.get('comments', '') # Adicionado campo comments
        duration_log = request.data.get('duration_minutes', 0) # Duração do treino real

        if rating is None:
            return Response({'detail': 'Avaliação (rating) é obrigatória.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating = int(rating)
            duration_log = int(duration_log)
        except ValueError:
            return Response({'detail': 'Avaliação e duração devem ser números inteiros.'}, status=status.HTTP_400_BAD_REQUEST)

        if rating < 1 or rating > 5:
            return Response({'detail': 'A avaliação (rating) deve estar entre 1 e 5.'}, status=status.HTTP_400_BAD_REQUEST)

        # Cria o log de treino (para duração e nota)
        WorkoutLog.objects.create(
            workout=workout,
            nota=rating,  # Mapeia 'rating' do frontend para 'nota' do backend
            duracao=duration_log
        )
        
        # Cria o feedback detalhado
        WorkoutFeedback.objects.create(
            user=request.user,
            workout=workout, # Associa o feedback diretamente ao treino
            workout_log=WorkoutLog.objects.filter(workout=workout).latest('created_at'), # Opcional: associa ao log mais recente
            rating=rating,
            comments=comments
        )

        try:
            workout_data_for_ai = {
                'carga': workout.carga,
                'intensity': workout.intensity,
                'series_reps': workout.series_reps
            }
            # Ajusta o treino com base no feedback usando a IA
            treino_ajustado = ajustar_treino_por_feedback(workout_data_for_ai, rating)
            
            workout.intensity = treino_ajustado.get('intensity', workout.intensity)
            workout.carga = treino_ajustado.get('carga', workout.carga)
            workout.series_reps = treino_ajustado.get('series_reps', workout.series_reps)
            workout.save()
        except Exception as e:
            print(f"Erro ao ajustar treino com IA no feedback: {str(e)}")
            # Não impede a resposta de sucesso se o ajuste da IA falhar

        serializer = WorkoutSerializer(workout)
        return Response(serializer.data)

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
    duration_minutes = serializer.validated_data.get('duration')
    muscle_groups = serializer.validated_data.get('muscle_groups')
    equipment = serializer.validated_data.get('equipment', [])
    intensity = serializer.validated_data.get('intensity', 'moderada') 

    # Construção do prompt para a IA
    prompt_parts = [
        f"Gere um treino de {workout_type} com duração de {duration_minutes} minutos para um nível {difficulty}.",
        f"Foque nos grupos musculares: {', '.join(muscle_groups) if muscle_groups else 'corpo inteiro'}."
    ]
    if equipment:
        prompt_parts.append(f"Utilize os seguintes equipamentos: {', '.join(equipment)}.")
    
    # Instruções para o formato JSON da IA
    prompt_parts.append("Retorne APENAS uma lista de exercícios em formato JSON. Cada exercício deve ser um objeto com as chaves 'id' (número), 'name' (string), 'sets' (string, ex: '3'), 'reps' (string, ex: '8-12' ou 'até a falha'), 'weight' (string, ex: '20kg' ou 'peso corporal'), 'duration' (string, ex: '30s' ou '0' se baseado em repetições), 'rest_time' (string, ex: '60s'), e 'instructions' (string).")
    prompt_parts.append("Não inclua nenhum texto adicional antes ou depois do JSON. Certifique-se de que o JSON é válido e não contém caracteres extras.")
    prompt = " ".join(prompt_parts)

    generated_exercises_list_of_dicts = []
    ai_response_content = ""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "Você é um treinador fitness que gera treinos detalhados em formato JSON. Responda APENAS com o JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7 # Adicionado para um pouco mais de criatividade, mas ainda consistente
        )
        
        ai_response_content = response.choices[0].message.content.strip()
        print(f"DEBUG - Resposta bruta da IA para treino: {ai_response_content}")

        # Tentar carregar o JSON. Remover qualquer texto antes/depois se a IA falhar.
        # Usa regex para encontrar o primeiro e último colchete para tentar extrair o JSON puro
        match = re.search(r'\[.*\]', ai_response_content, re.DOTALL)
        if match:
            json_string = match.group(0)
            generated_exercises_list_of_dicts = json.loads(json_string)
        else:
            raise json.JSONDecodeError("JSON não encontrado na resposta da IA", ai_response_content, 0)
        
        # Adiciona IDs sequenciais se a IA não os forneceu ou para garantir unicidade
        for i, exercise in enumerate(generated_exercises_list_of_dicts):
            if 'id' not in exercise:
                exercise['id'] = i + 1

    except json.JSONDecodeError as e:
        print(f"ERRO - Falha ao decodificar JSON da IA para treino: {e}")
        print(f"ERRO - Conteúdo que causou o erro: {ai_response_content}")
        # Fallback robusto em caso de falha na IA
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

    exercises_json_str = json.dumps(generated_exercises_list_of_dicts)

    # Cria um nome e descrição baseados nos parâmetros de entrada
    workout_name = f"{workout_type.capitalize()} - {difficulty.capitalize()} ({duration_minutes}min)"
    workout_description = f"Este treino de {workout_type} de {duration_minutes} minutos é projetado para o nível {difficulty}, focando em {', '.join(muscle_groups) if muscle_groups else 'corpo inteiro'}."
    if equipment:
        workout_description += f" Equipamentos: {', '.join(equipment)}."

    workout = Workout.objects.create(
        user=user,
        workout_type=workout_type,
        intensity=intensity, 
        duration=timedelta(minutes=duration_minutes),
        carga=20, # Valor padrão, pode ser ajustado pela IA no futuro
        frequency='3x por semana', # Valor padrão, pode ser ajustado pela IA no futuro
        exercises=exercises_json_str, 
        series_reps='3x12', # Valor padrão, pode ser ajustado pela IA no futuro
        focus= ', '.join(muscle_groups) if muscle_groups else 'fullbody', # CORREÇÃO: Converte a lista para string para o campo 'focus'
        
        # Novos campos populados
        name=workout_name,
        description=workout_description,
        difficulty=difficulty,
        muscle_groups=muscle_groups, # Salva a lista de grupos musculares
        equipment=equipment, # Salva a lista de equipamentos
        rating=None, # Inicia sem avaliação
        completed_date=None, # Inicia sem data de conclusão
        status='pending', # Inicia como pendente
    )

    return Response({
        'detail': 'Treino criado com sucesso!',
        'workout': WorkoutSerializer(workout).data # Retorna o treino serializado completo
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_workout(request):
    """
    Registra um treino existente no banco de dados.
    (Este endpoint pode ser usado para salvar um treino gerado ou um treino manual).
    """
    data = request.data.copy()
    serializer = WorkoutSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({'detail': 'Treino registrado com sucesso!', 'workout': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Este endpoint parece ser um duplicado ou uma versão antiga do feedback no ViewSet.
# Recomenda-se usar o @action feedback no WorkoutViewSet para consistência.
# No entanto, se for mantido, ele precisa criar um WorkoutFeedback, não apenas um WorkoutLog.
# Mantido por enquanto, mas com a lógica de feedback ajustada.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_workout_feedback(request, workout_id):
    """
    Envia feedback para um treino específico.
    Cria um WorkoutFeedback e um WorkoutLog (para duração).
    """
    try:
        workout = Workout.objects.get(id=workout_id, user=request.user)
    except Workout.DoesNotExist:
        return Response({'detail': 'Treino não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    rating = request.data.get('rating')
    duration_minutes = request.data.get('duration_minutes')
    comments = request.data.get('comments', '') # Adicionado campo comments

    if rating is None or duration_minutes is None:
        return Response({'detail': 'Avaliação e duração são obrigatórias.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        rating = int(rating)
        duration_minutes = int(duration_minutes)
    except ValueError:
        return Response({'detail': 'Avaliação e duração devem ser números inteiros.'}, status=status.HTTP_400_BAD_REQUEST)

    if rating < 1 or rating > 5:
        return Response({'detail': 'A avaliação deve estar entre 1 e 5.'}, status=status.HTTP_400_BAD_REQUEST)

    # Cria o log de treino
    WorkoutLog.objects.create(workout=workout, nota=rating, duracao=duration_minutes)

    # Cria o feedback detalhado
    WorkoutFeedback.objects.create(
        user=request.user,
        workout=workout,
        workout_log=WorkoutLog.objects.filter(workout=workout).latest('created_at'), # Opcional: associa ao log mais recente
        rating=rating,
        comments=comments
    )

    # Opcional: ajustar o treino com IA aqui também, se desejar que este endpoint também o faça.
    # try:
    #     workout_data_for_ai = {
    #         'carga': workout.carga,
    #         'intensity': workout.intensity,
    #         'series_reps': workout.series_reps
    #     }
    #     treino_ajustado = ajustar_treino_por_feedback(workout_data_for_ai, rating)
    #     workout.intensity = treino_ajustado.get('intensity', workout.intensity)
    #     workout.carga = treino_ajustado.get('carga', workout.carga)
    #     workout.series_reps = treino_ajustado.get('series_reps', workout.series_reps)
    #     workout.save()
    # except Exception as e:
    #     print(f"Erro ao ajustar treino com IA no feedback (send_workout_feedback): {str(e)}")

    return Response({'detail': 'Feedback registrado com sucesso!'}, status=status.HTTP_201_CREATED)
