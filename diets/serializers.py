from datetime import timedelta
from rest_framework import serializers
from .models import Diet, Workout, DietFeedback


class DietSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diet
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class WorkoutSerializer(serializers.ModelSerializer):
    duration_display = serializers.SerializerMethodField()

    class Meta:
        model = Workout
        fields = [
            'id',
            'workout_type',
            'intensity',
            'duration',           # usado para criar/editar
            'duration_display',   # usado para exibir formatado
            'created_at',
            'exercises',
            'series_reps',
            'frequency',
            'carga'
        ]
        read_only_fields = ['id', 'created_at', 'user', 'duration_display']

    def get_duration_display(self, obj):
        if isinstance(obj.duration, timedelta):
            total_seconds = int(obj.duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            if hours > 0:
                return f"{hours}h {minutes}min"
            return f"{minutes} min"
        return None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DietFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietFeedback
        fields = ['id', 'user', 'diet', 'rating', 'feedback_text', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
