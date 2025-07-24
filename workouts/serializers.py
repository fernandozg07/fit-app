# workouts/serializers.py

from rest_framework import serializers
from .models import Workout, WorkoutLog, WorkoutFeedback 
from datetime import timedelta
import json # IMPORTANTE: Importar a biblioteca json

class WorkoutSerializer(serializers.ModelSerializer):
    duration_display = serializers.SerializerMethodField()
    exercises = serializers.SerializerMethodField() # Tratar exercises como um campo de método

    class Meta:
        model = Workout
        fields = [
            'id', 'user', 'workout_type', 'intensity', 'duration',
            'duration_display', 'created_at', 'exercises', 'series_reps',
            'frequency', 'carga', 'focus',
        ]
        read_only_fields = ['id', 'created_at', 'duration_display', 'user']

    def get_duration_display(self, obj):
        if isinstance(obj.duration, timedelta):
            total_seconds = int(obj.duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours}h {minutes}min" if hours > 0 else f"{minutes} min"
        return None

    # FIX: Método para DESERIALIZAR a string JSON de exercises em um array de objetos Python
    def get_exercises(self, obj):
        if obj.exercises:
            try:
                # Tenta carregar a string JSON.
                return json.loads(obj.exercises)
            except json.JSONDecodeError:
                # Se houver um erro de decodificação JSON (porque é uma string simples de um treino antigo),
                # tenta dividir a string por vírgulas e retornar uma lista de strings.
                # Isso é um fallback para dados antigos, mas o ideal é que o `generate_workout` SEMPRE salve JSON.
                return [{"id": i, "name": e.strip(), "sets": 0, "reps": 0, "rest_time": 0, "instructions": ""} for i, e in enumerate(obj.exercises.split(','))]
        return []

class WorkoutLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutLog
        fields = ['id', 'workout', 'nota', 'duracao', 'created_at']

class WorkoutFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutFeedback
        fields = ['id', 'user', 'workout_log', 'rating', 'comments', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']


class WorkoutGenerateInputSerializer(serializers.Serializer):
    workout_type = serializers.CharField(max_length=50, required=True)
    difficulty = serializers.CharField(max_length=50, required=True)
    duration = serializers.IntegerField(required=True, help_text="Duração em minutos")
    muscle_groups = serializers.ListField(child=serializers.CharField(max_length=50), required=True)
    equipment = serializers.ListField(child=serializers.CharField(max_length=50), required=False)
    focus = serializers.CharField(max_length=50, required=False)
    intensity = serializers.CharField(max_length=50, required=False)

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
