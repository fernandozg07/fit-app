from rest_framework import serializers
from .models import Workout, WorkoutLog, WorkoutFeedback
from datetime import timedelta

class WorkoutSerializer(serializers.ModelSerializer):
    duration_display = serializers.SerializerMethodField()

    class Meta:
        model = Workout
        fields = [
            'id', 'user', 'workout_type', 'intensity', 'duration',
            'duration_display', 'created_at', 'exercises', 'series_reps',
            'frequency', 'carga',
        ]
        read_only_fields = ['id', 'created_at', 'duration_display', 'user']

    def get_duration_display(self, obj):
        if isinstance(obj.duration, timedelta):
            total_seconds = int(obj.duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours}h {minutes}min" if hours > 0 else f"{minutes} min"
        return None

class WorkoutLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutLog
        fields = ['id', 'workout', 'nota', 'duracao', 'created_at']

class WorkoutFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutFeedback
        fields = ['id', 'user', 'workout_log', 'rating', 'comments', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']
