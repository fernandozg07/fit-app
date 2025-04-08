from rest_framework import serializers
from .models import Diet, DietFeedback, Workout

class DietSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diet
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class DietFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietFeedback
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = '__all__'
        read_only_fields = ['user', 'created_at']
