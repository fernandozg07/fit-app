from rest_framework import serializers
from .models import Workout
from datetime import timedelta


class WorkoutSerializer(serializers.ModelSerializer):
    duration_display = serializers.SerializerMethodField()

    class Meta:
        model = Workout
        fields = [
            'id',
            'workout_type',
            'intensity',
            'duration',
            'duration_display',
            'created_at',
            'exercises',
            'series_reps',
            'frequency',
            'carga',
        ]
        read_only_fields = ['id', 'created_at', 'duration_display']

    def get_duration_display(self, obj):
        if isinstance(obj.duration, timedelta):
            total_seconds = int(obj.duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            if hours > 0:
                return f"{hours}h {minutes}min"
            return f"{minutes} min"
        return None

class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = '__all__'

# Adicione esse:
class WorkoutLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = ['id', 'user', 'date', 'exercises', 'notes', 'load']  # ajuste conforme seu model