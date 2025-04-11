from rest_framework import serializers
from .models import Diet, DietFeedback
from django.utils import timezone

class DietSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diet
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, data):
        user = self.context['request'].user
        meal = data['meal']
        date = data.get('date', timezone.now().date())

        if Diet.objects.filter(user=user, meal=meal, date=date).exists():
            raise serializers.ValidationError("Essa refeição já foi registrada hoje.")
        return data

class DietFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietFeedback
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("A nota deve estar entre 1 e 5.")
        return value
