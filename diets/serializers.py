from rest_framework import serializers
from .models import Diet, DietFeedback
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator # FIX: Importado validadores do Django

class DietSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diet
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, data):
        user = self.context['request'].user
        meal = data.get('meal') 
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

# NOVO SERIALIZER PARA ENTRADA DE DADOS DA GERAÇÃO DE DIETA
class DietGenerateInputSerializer(serializers.Serializer):
    goal = serializers.CharField(max_length=100, required=True)
    # FIX: Usando MinValueValidator importado de django.core.validators
    calories_target = serializers.IntegerField(required=True, validators=[MinValueValidator(1)])
    # FIX: Usando MinValueValidator e MaxValueValidator importados de django.core.validators
    meals_count = serializers.IntegerField(required=True, validators=[MinValueValidator(1), MaxValueValidator(6)]) 
    dietary_restrictions = serializers.ListField(
        child=serializers.CharField(max_length=100), 
        required=False, 
        allow_empty=True
    )

    def validate_goal(self, value):
        valid_goals = ['perda de peso', 'ganho de massa muscular', 'manutenção']
        if value.lower() not in valid_goals:
            raise serializers.ValidationError(f"Objetivo inválido. Opções válidas: {', '.join(valid_goals)}")
        return value
