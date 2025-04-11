from openai import OpenAI
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from workouts.models import Workout
from progress.models import ProgressEntry
from chatbot.models import ChatMessage
from ai import trainer
from decouple import config
from datetime import datetime

# Cliente OpenAI para OpenRouter
client = OpenAI(
    api_key=config("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"  # Essencial para funcionar com OpenRouter
)

def chamar_openai(mensagem):
    """Fallback com OpenAI caso a IA personalizada não trate a pergunta"""
    try:
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um treinador fitness inteligente e motivador."},
                {"role": "user", "content": mensagem}
            ],
            max_tokens=150
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro ao chamar a OpenAI: {str(e)}"

def gerar_resposta_inteligente(user, mensagem):
    """Responde com base nos dados do usuário + fallback IA"""
    msg = mensagem.lower()

    try:
        if "peso atual" in msg:
            ultimo = ProgressEntry.objects.filter(user=user).order_by('-date').first()
            if ultimo:
                return f"Seu peso atual registrado é {ultimo.weight} kg em {ultimo.date.strftime('%d/%m/%Y')}."
            return "Você ainda não registrou nenhum peso no sistema."

        elif any(x in msg for x in ["treino de pernas", "sugestão de treino", "quero um treino"]):
            treino_existente = Workout.objects.filter(user=user, focus="pernas").order_by('-created_at').first()
            if treino_existente:
                return f"Seu último treino de pernas foi: {treino_existente.exercises}."

            sugestao = "Agachamento, Leg Press, Cadeira Extensora"
            Workout.objects.create(
                user=user,
                workout_type="musculacao",
                focus="pernas",
                exercises=sugestao,
                duration=45,
                intensity="Alta",
                frequency="3x por semana",
                series_reps="3x12",
                carga=60,
                load="media"
            )
            return f"Gerei e salvei um treino de pernas para você: {sugestao}"

        elif "carga" in msg and "rosca direta" in msg:
            treino = Workout.objects.filter(user=user, exercises__icontains="rosca direta").order_by('-created_at').first()
            if treino and treino.carga:
                return f"Você costuma usar cerca de {treino.carga} kg para rosca direta."
            return "Ainda não encontrei registros de rosca direta nos seus treinos."

        elif any(x in msg for x in ["carga ideal", "carga sugerida"]):
            historico = Workout.objects.filter(user=user, focus="pernas").order_by('-created_at')[:5]
            cargas = [
                float(t.carga) for t in historico if t.carga and str(t.carga).replace('.', '', 1).isdigit()
            ]

            if not cargas:
                return "Não foi possível calcular a carga ideal por falta de dados recentes."

            sugestao = trainer.ajustar_treino([{"carga": c} for c in cargas])
            return f"Sugestão de carga para treino de pernas: {sugestao['carga']} kg com {sugestao['reps']} repetições."

        return chamar_openai(mensagem)

    except Exception as e:
        return f"Houve um erro ao processar a mensagem: {str(e)}"

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_ai(request):
    """Chat com IA baseado nos dados do usuário"""
    user = request.user
    user_message = request.data.get('user_message', '').strip()

    if not user_message:
        return Response({'error': 'A mensagem não pode estar vazia.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        bot_response = gerar_resposta_inteligente(user, user_message)

        ChatMessage.objects.create(
            user=user,
            user_message=user_message,
            bot_response=bot_response
        )

        return Response({'response': bot_response}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
