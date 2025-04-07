import openai
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

# Definindo a chave da API do OpenAI
openai.api_key = config("OPENAI_API_KEY")

def chamar_openai(mensagem):
    try:
        # Usando o novo método da API do OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Modelo recomendado (pode ser "gpt-4")
            messages=[{"role": "user", "content": mensagem}],
            max_tokens=150
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Erro ao chamar a OpenAI: {str(e)}"

def gerar_resposta_inteligente(user, mensagem):
    msg = mensagem.lower()

    if "peso atual" in msg:
        ultimo = ProgressEntry.objects.filter(user=user).order_by('-date').first()
        if ultimo:
            data_formatada = ultimo.date.strftime('%d/%m/%Y')
            return f"Seu peso atual registrado é {ultimo.weight} kg em {data_formatada}."
        return "Você ainda não registrou nenhum peso."

    elif "treino de pernas" in msg or "sugestão de treino" in msg or "quero um treino" in msg:
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
        return f"Gerei um treino de pernas com base no seu objetivo e já salvei: {sugestao}"

    elif "carga" in msg and "rosca direta" in msg:
        treino = Workout.objects.filter(user=user, exercises__icontains="rosca direta").order_by('-created_at').first()
        if treino:
            return f"Você costuma usar cerca de {treino.carga} kg para rosca direta."
        return "Ainda não encontrei registros de rosca direta nos seus treinos."

    elif "carga ideal" in msg or "carga sugerida" in msg:
        historico = Workout.objects.filter(user=user, focus="pernas").order_by('-created_at')[:5]
        historico_treinos = []

        for treino in historico:
            try:
                carga_num = float(treino.carga)
                historico_treinos.append({"carga": carga_num})
            except (ValueError, TypeError):
                continue

        sugestao = trainer.ajustar_treino(historico_treinos)
        return f"Sugestão de carga para treino de pernas: {sugestao['carga']} kg para {sugestao['reps']} repetições."

    else:
        return chamar_openai(mensagem)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_ai(request):
    user = request.user
    user_message = request.data.get('user_message', '').strip()

    if not user_message:
        return Response({'error': 'A mensagem não pode estar vazia.'}, status=status.HTTP_400_BAD_REQUEST)

    bot_response = gerar_resposta_inteligente(user, user_message)

    # Salvando a mensagem do usuário e a resposta do bot no banco
    ChatMessage.objects.create(
        user=user,
        user_message=user_message,
        bot_response=bot_response
    )

    return Response({'response': bot_response}, status=status.HTTP_200_OK)
