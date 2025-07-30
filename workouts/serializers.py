from rest_framework import serializers
from .models import Workout, WorkoutLog, WorkoutFeedback
from datetime import timedelta
import json
import re

class WorkoutSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Workout.
    Inclui campos para exibir duração formatada e exercícios deserializados.
    """
    duration_display = serializers.SerializerMethodField(help_text="Duração do treino formatada para exibição.")
    exercises = serializers.SerializerMethodField(help_text="Lista de objetos de exercícios detalhados.") 
    muscle_groups = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True, help_text="Lista de grupos musculares alvo.")
    equipment = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True, help_text="Lista de equipamentos necessários.")

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
        Formata a duração do treino para exibição amigável (ex: '45 min', '1h 30min').
        Lida com objetos timedelta e strings no formato "PTxxM".
        """
        if isinstance(obj.duration, timedelta):
            total_seconds = int(obj.duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours}h {minutes}min" if hours > 0 else f"{minutes} min"
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
        Deserializa a string JSON de exercises em uma lista de objetos de exercício.
        Fornece um fallback para strings simples de treinos antigos.
        """
        if obj.exercises:
            try:
                return json.loads(obj.exercises)
            except json.JSONDecodeError:
                return [
                    {
                        "id": i,
                        "name": e.strip(),
                        "sets": "0", 
                        "reps": "0", 
                        "weight": "0", 
                        "duration": "0", 
                        "rest_time": "0", 
                        "instructions": "Nenhuma instrução disponível."
                    }
                    for i, e in enumerate(obj.exercises.split(','))
                ]
        return []

class WorkoutLogSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo WorkoutLog.
    Inclui o novo campo 'exercise_logs'.
    """
    class Meta:
        model = WorkoutLog
        fields = ['id', 'workout', 'nota', 'duracao', 'exercise_logs', 'created_at'] # Adicionado 'exercise_logs'
        read_only_fields = ['id', 'created_at']

class WorkoutFeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo WorkoutFeedback.
    Adicionado 'duration_minutes' e 'exercise_logs' para receber do frontend.
    """
    duration_minutes = serializers.IntegerField(write_only=True, required=False, help_text="Duração real do treino em minutos.")
    # Removido 'carga_utilizada' e adicionado 'exercise_logs' para detalhamento por exercício
    exercise_logs = serializers.JSONField(write_only=True, required=False, help_text="Detalhes de séries, repetições e carga por exercício.")

    class Meta:
        model = WorkoutFeedback
        fields = ['id', 'user', 'workout', 'workout_log', 'rating', 'comments', 'created_at', 'duration_minutes', 'exercise_logs'] # Atualizado fields
        read_only_fields = ['id', 'created_at', 'user', 'workout', 'workout_log']

    def create(self, validated_data):
        duration_minutes = validated_data.pop('duration_minutes', 0) 
        exercise_logs = validated_data.pop('exercise_logs', []) # Remove do validated_data para não tentar salvar no WorkoutFeedback
        
        workout = self.context.get('workout')
        workout_log = self.context.get('workout_log')

        # Cria o feedback
        feedback = WorkoutFeedback.objects.create(
            user=self.context['request'].user,
            workout=workout,
            workout_log=workout_log,
            **validated_data
        )
        return feedback


class WorkoutGenerateInputSerializer(serializers.Serializer):
    """
    Serializer para validar os dados de entrada para a geração de treino pela IA.
    """
    workout_type = serializers.CharField(max_length=50, required=True, help_text="Tipo de treino (e.g., musculacao, cardio).")
    difficulty = serializers.CharField(max_length=50, required=True, help_text="Nível de dificuldade (e.g., iniciante, intermediario).")
    duration = serializers.IntegerField(required=True, help_text="Duração do treino em minutos.")
    muscle_groups = serializers.ListField(child=serializers.CharField(max_length=50), required=True, help_text="Lista de grupos musculares alvo.")
    equipment = serializers.ListField(child=serializers.CharField(max_length=50), required=False, allow_empty=True, help_text="Lista de equipamentos disponíveis.")
    focus = serializers.CharField(max_length=50, required=False, allow_blank=True, help_text="Foco principal do treino (opcional, pode ser inferido).")
    intensity = serializers.CharField(max_length=50, required=False, allow_blank=True, help_text="Intensidade desejada (e.g., moderada, alta).")

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("A duração deve ser um número positivo de minutos.")
        return value

    def validate_difficulty(self, value):
        valid_difficulties = ['iniciante', 'intermediario', 'avancado']
        if value.lower() not in valid_difficulties:
            raise serializers.ValidationError(f"Dificuldade inválida. Opções válidas: {', '.join(valid_difficulties)}")
        return value

    def validate_workout_type(self, value):
        valid_types = ['musculacao', 'cardio', 'flexibilidade', 'yoga', 'strength', 'hiit']
        if value.lower() not in valid_types:
            raise serializers.ValidationError(f"Tipo de treino inválido. Opções válidas: {', '.join(valid_types)}")
        return value
