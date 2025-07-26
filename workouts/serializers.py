from rest_framework import serializers
from .models import Workout, WorkoutLog, WorkoutFeedback
from datetime import timedelta
import json
import re

class WorkoutSerializer(serializers.ModelSerializer):
    duration_display = serializers.SerializerMethodField()
    exercises = serializers.SerializerMethodField() # Para retornar a lista de objetos Python

    class Meta:
        model = Workout
        fields = [
            'id', 'user', 'workout_type', 'intensity', 'duration',
            'duration_display', 'created_at', 'exercises', 'series_reps',
            'frequency', 'carga', 'focus',
            'muscle_groups', 'equipment', 
            'description', 'difficulty', 
            'name', 'rating', 'completed_date', 'status', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'duration_display', 'user', 'updated_at']

    def get_duration_display(self, obj):
        """
        Formata a duração do treino para exibição amigável.
        Lida com objetos timedelta e strings no formato "PTxxM".
        """
        if isinstance(obj.duration, timedelta):
            total_seconds = int(obj.duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours}h {minutes}min" if hours > 0 else f"{minutes} min"
        # Fallback para strings, caso a duração venha em um formato como "PT45M"
        if isinstance(obj.duration, str):
            try:
                match = re.search(r'PT(\d+)M', obj.duration)
                if match:
                    minutes = int(match.group(1))
                    return f"{minutes} min"
            except Exception:
                pass 
        return None

    def get_exercises(self, obj):
        """
        Deserializa a string JSON de exercises em uma lista de objetos Exercise.
        Fornece um fallback para strings simples de treinos antigos.
        """
        if obj.exercises:
            try:
                # Tenta carregar a string JSON.
                return json.loads(obj.exercises)
            except json.JSONDecodeError:
                # Fallback para strings simples (e.g., "Corrida, Flexões")
                # Converte para o formato de objeto Exercise esperado pelo frontend.
                return [
                    {
                        "id": i,
                        "name": e.strip(),
                        "sets": "0", # Alterado para string para consistência com a interface Exercise
                        "reps": "0", # Alterado para string
                        "weight": "0", # Alterado para string
                        "duration": "0", # Alterado para string
                        "rest_time": "0", # Alterado para string
                        "instructions": "Nenhuma instrução disponível."
                    }
                    for i, e in enumerate(obj.exercises.split(','))
                ]
        return []

class WorkoutLogSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo WorkoutLog.
    """
    class Meta:
        model = WorkoutLog
        fields = ['id', 'workout', 'nota', 'duracao', 'created_at']

class WorkoutFeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo WorkoutFeedback.
    """
    class Meta:
        model = WorkoutFeedback
        fields = ['id', 'user', 'workout', 'workout_log', 'rating', 'comments', 'created_at'] # Adicionado 'workout'
        read_only_fields = ['id', 'created_at', 'user']

class WorkoutGenerateInputSerializer(serializers.Serializer):
    """
    Serializer para validar os dados de entrada para a geração de treino pela IA.
    """
    workout_type = serializers.CharField(max_length=50, required=True)
    difficulty = serializers.CharField(max_length=50, required=True)
    duration = serializers.IntegerField(required=True, help_text="Duração em minutos")
    muscle_groups = serializers.ListField(child=serializers.CharField(max_length=50), required=True)
    equipment = serializers.ListField(child=serializers.CharField(max_length=50), required=False, allow_empty=True) # Permitir vazio
    focus = serializers.CharField(max_length=50, required=False, allow_blank=True) # Permitir em branco
    intensity = serializers.CharField(max_length=50, required=False, allow_blank=True) # Permitir em branco

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("A duração deve ser um número positivo de minutos.")
        return value

    def validate_difficulty(self, value):
        valid_difficulties = ['iniciante', 'moderado', 'avancado']
        if value.lower() not in valid_difficulties:
            raise serializers.ValidationError(f"Dificuldade inválida. Opções válidas: {', '.join(valid_difficulties)}")
        return value

    def validate_workout_type(self, value):
        valid_types = ['musculacao', 'cardio', 'flexibilidade', 'yoga']
        if value.lower() not in valid_types:
            raise serializers.ValidationError(f"Tipo de treino inválido. Opções válidas: {', '.join(valid_types)}")
        return value

