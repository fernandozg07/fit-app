def ajustar_treino(historico_treinos):
    """
    Função para ajustar a carga de treino baseada no histórico de treinos.
    """
    if len(historico_treinos) > 0:
        carga_media = sum([treino["carga"] for treino in historico_treinos]) / len(historico_treinos)
        carga_ideal = carga_media * 1.1
        return {"carga": carga_ideal, "reps": 10}
    return {"carga": 50, "reps": 10}
