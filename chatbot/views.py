# chatbot/views.py

from openai import OpenAI
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from workouts.models import Workout
from progress.models import ProgressEntry
from chatbot.models import ChatMessage
from ai import trainer # Importando o módulo trainer
from decouple import config
from datetime import datetime, timedelta # Importar timedelta para duration

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
            return "Você ainda não registrou nenhum peso no sistema. Que tal registrar seu primeiro peso na seção de Progresso?"

        # FIX: Removida a criação direta de Workout e ajustada a resposta para ser textual
        elif any(x in msg for x in ["treino de pernas", "sugestão de treino", "quero um treino"]):
            treino_existente = Workout.objects.filter(user=user, focus="pernas").order_by('-created_at').first()
            if treino_existente:
                return f"Seu último treino de pernas foi: {treino_existente.exercises}. Se quiser um novo, posso te ajudar a gerar um na seção de Treinos."
            
            return "Posso te ajudar a gerar um treino personalizado! Por favor, vá para a seção 'Treinos' e use a funcionalidade de 'Novo Treino' para me dar mais detalhes sobre o que você procura."

        elif "carga" in msg and "rosca direta" in msg:
            treino = Workout.objects.filter(user=user, exercises__icontains="rosca direta").order_by('-created_at').first()
            if treino and treino.carga:
                return f"Você costuma usar cerca de {treino.carga} kg para rosca direta."
            return "Ainda não encontrei registros de rosca direta nos seus treinos. Que tal registrar seus treinos para que eu possa te dar sugestões mais precisas?"

        elif any(x in msg for x in ["carga ideal", "carga sugerida"]):
            historico = Workout.objects.filter(user=user, focus="pernas").order_by('-created_at')[:5]
            cargas = [
                float(t.carga) for t in historico if t.carga and str(t.carga).replace('.', '', 1).isdigit()
            ]

            if not cargas:
                return "Não foi possível calcular a carga ideal por falta de dados recentes. Por favor, registre mais treinos para que eu possa te ajudar."

            # Usando a função ajustar_treino do módulo ai.trainer
            sugestao = trainer.ajustar_treino([{"carga": c} for c in cargas])
            return f"Sugestão de carga para treino de pernas: {sugestao['carga']} kg com {sugestao['reps']} repetições."

        return chamar_openai(mensagem)

    except Exception as e:
        # Logar o erro para depuração
        print(f"Erro em gerar_resposta_inteligente: {e}")
        return f"Houve um erro ao processar a mensagem. Por favor, tente novamente mais tarde."

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
        # Logar o erro para depuração
        print(f"Erro na view chat_ai: {e}")
        return Response({'error': f"Erro interno do servidor ao processar sua mensagem. Por favor, tente novamente mais tarde."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
