# chatbot/views.py

import openai
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from workouts.models import Workout
from progress.models import ProgressEntry
from chatbot.models import ChatMessage
from ai import trainer # Importando o módulo trainer
from decouple import config
from datetime import datetime, timedelta
import json # Importar a biblioteca json

# Configuração OpenAI
try:
    openai.api_key = config("OPENAI_API_KEY", default="")
    if openai.api_key:
        openai.api_base = "https://openrouter.ai/api/v1"
except Exception as e:
    print(f"Erro na configuração da OpenAI: {e}")

def chamar_openai(mensagem):
    """Fallback com OpenAI caso a IA personalizada não trate a pergunta"""
    try:
        if not openai.api_key:
            return "Desculpe, o serviço de IA não está disponível no momento. Como posso ajudá-lo de outra forma?"
        
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um treinador fitness inteligente e motivador."},
                {"role": "user", "content": mensagem}
            ],
            max_tokens=150
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erro ao chamar OpenAI: {e}")
        return "Desculpe, não consegui processar sua pergunta no momento. Tente novamente mais tarde ou seja mais específico."

def gerar_resposta_inteligente(user, mensagem):
    """Responde com base nos dados do usuário + fallback IA"""
    msg = mensagem.lower()

    try:
        if "peso atual" in msg:
            ultimo = ProgressEntry.objects.filter(user=user).order_by('-date').first()
            if ultimo:
                return f"Seu peso atual registrado é {ultimo.weight} kg em {ultimo.date.strftime('%d/%m/%Y')}."
            return "Você ainda não registrou nenhum peso no sistema. Que tal registrar seu primeiro peso na seção de Progresso?"

        elif any(x in msg for x in ["treino de pernas", "sugestão de treino", "quero um treino"]):
            treino_existente = Workout.objects.filter(user=user, focus="lower_body").order_by('-created_at').first()
            if treino_existente:
                # FIX: Deserializar a string JSON de exercises para exibir corretamente
                try:
                    exercises_data = json.loads(treino_existente.exercises)
                    exercise_names = ", ".join([ex['name'] for ex in exercises_data])
                except json.JSONDecodeError:
                    exercise_names = treino_existente.exercises # Fallback se não for JSON válido
                return f"Seu último treino de pernas foi: {exercise_names}. Se quiser um novo, posso te ajudar a gerar um na seção de Treinos."
            
            return "Posso te ajudar a gerar um treino personalizado! Por favor, vá para a seção 'Treinos' e use a funcionalidade de 'Novo Treino' para me dar mais detalhes sobre o que você procura."

        elif "carga" in msg and "rosca direta" in msg:
            treino = Workout.objects.filter(user=user, exercises__icontains="rosca direta").order_by('-created_at').first()
            if treino and treino.carga:
                return f"Você costuma usar cerca de {treino.carga} kg para rosca direta."
            return "Ainda não encontrei registros de rosca direta nos seus treinos. Que tal registrar seus treinos para que eu possa te dar sugestões mais precisas?"

        elif any(x in msg for x in ["carga ideal", "carga sugerida"]):
            historico = Workout.objects.filter(user=user, focus="lower_body").order_by('-created_at')[:5]
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

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def chat_ai(request):
    """Chat simples sem IA para evitar erros"""
    user = request.user
    
    if request.method == 'GET':
        # Retorna lista vazia por enquanto para evitar erros de banco
        return Response([], status=status.HTTP_200_OK)
    
    # POST - Enviar nova mensagem
    user_message = request.data.get('message', '').strip() 

    if not user_message:
        return Response({'error': 'A mensagem não pode estar vazia.'}, status=status.HTTP_400_BAD_REQUEST)

    # Resposta simples baseada em palavras-chave
    bot_response = "Obrigado pela sua mensagem! Estou aqui para ajudar."
    
    msg_lower = user_message.lower()
    if 'peso' in msg_lower:
        bot_response = "Para acompanhar seu peso, use a seção de Progresso."
    elif 'treino' in msg_lower:
        bot_response = "Use a seção de Treinos para gerar um plano personalizado."
    elif 'dieta' in msg_lower:
        bot_response = "Acesse a seção de Dietas para gerar um plano alimentar."
    elif 'oi' in msg_lower or 'olá' in msg_lower:
        bot_response = "Olá! Como posso ajudar com seu fitness hoje?"

    # Retorna resposta sem salvar no banco por enquanto
    return Response({
        'id': 1,
        'user_message': user_message,
        'bot_response': bot_response,
        'created_at': '2024-01-01T00:00:00Z'
    }, status=status.HTTP_200_OK)
