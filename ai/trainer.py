# ai/trainer.py

def ajustar_treino_por_feedback(workout_data, rating):
    """
    Ajusta os parâmetros de um treino (carga, intensidade, séries/reps)
    com base no feedback de rating.
    
    Args:
        workout_data (dict): Um dicionário contendo os dados atuais do treino,
                             como 'carga', 'intensity', 'series_reps'.
        rating (int): A nota de feedback dada ao treino (1 a 5).
        
    Returns:
        dict: Um dicionário com os parâmetros do treino ajustados.
    """
    carga = workout_data.get('carga', 50)
    intensity = workout_data.get('intensity', 'moderada')
    series_reps = workout_data.get('series_reps', '3x10')

    # Lógica de ajuste baseada no rating
    if rating >= 4: # Bom feedback: aumentar carga/intensidade
        carga = round(carga * 1.05) # Aumenta 5% da carga
        if intensity == 'moderada':
            intensity = 'alta'
        # Poderia adicionar lógica para aumentar reps ou séries aqui
    elif rating <= 2: # Mau feedback: diminuir carga/intensidade
        carga = round(carga * 0.95) # Diminui 5% da carga
        if intensity == 'alta':
            intensity = 'moderada'
        # Poderia adicionar lógica para diminuir reps ou séries aqui
    
    # Garante que a carga não seja negativa
    carga = max(0, carga)

    return {
        "carga": carga,
        "intensity": intensity,
        "series_reps": series_reps # Mantido como está por enquanto, pode ser ajustado com mais lógica
    }

# A função original 'ajustar_treino' que usa histórico pode ser mantida
# se tiver um propósito diferente (ex: sugerir novo treino baseado em histórico geral).
# Caso contrário, pode ser removida se 'ajustar_treino_por_feedback' a substitui.
# def ajustar_treino(historico_treinos):
#     """
#     Função para ajustar a carga de treino baseada no histórico de treinos.
#     """
#     if len(historico_treinos) > 0:
#         carga_media = sum([treino["carga"] for treino in historico_treinos]) / len(historico_treinos)
#         carga_ideal = carga_media * 1.1
#         return {"carga": carga_ideal, "reps": 10}
#     return {"carga": 50, "reps": 10}
