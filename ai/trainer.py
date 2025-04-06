import numpy as np

def ajustar_treino(historico_treinos):
    """
    Função para ajustar a carga de treino baseada no histórico de treinos.
    Aqui você pode implementar a lógica de ajuste real conforme os dados do usuário.
    """
    # Exemplo simples de ajuste de carga baseado no histórico de treinos
    if len(historico_treinos) > 0:
        carga_media = sum([treino["carga"] for treino in historico_treinos]) / len(historico_treinos)
        carga_ideal = carga_media * 1.1  # Aumenta a carga em 10% como exemplo
        return {"carga": carga_ideal, "reps": 10}  # Retorna sugestão de carga e repetições
    return {"carga": 50, "reps": 10}  # Valor padrão