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
            'duration',           # Para criação/edição
            'duration_display',   # Para exibição legível
            'created_at',
            'exercises',
            'series_reps',
            'frequency',
            'carga',              # ✅ Campo adicionado
        ]
        read_only_fields = ['id', 'created_at', 'duration_display']

    def get_duration_display(self, obj):
        """
        Converte timedelta em formato legível como '1h 30min' ou '45 min'.
        """
        if isinstance(obj.duration, timedelta):
            total_seconds = int(obj.duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            if hours > 0:
                return f"{hours}h {minutes}min"
            return f"{minutes} min"
        return None
