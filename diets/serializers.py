from rest_framework import serializers
from .models import Diet, DietFeedback, MEAL_CHOICES, GOAL_CHOICES
from django.core.validators import MinValueValidator, MaxValueValidator

class DietSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diet
        fields = [
            'id', 'user', 'meal', 'calories', 'protein', 'carbs', 'fat', 'date',
            'created_at', 'updated_at',
            'name', 'description', 'ingredients', 'preparation_time_minutes',
            'goal', 'dietary_restrictions', 'preferred_cuisine',
            'target_calories', 'target_protein', 'target_carbs', 'target_fat', 'water_intake_ml', 'rating'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

class DietFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietFeedback
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("A nota (rating) deve estar entre 1 e 5.")
        return value

class DietGenerateInputSerializer(serializers.Serializer):
    goal = serializers.ChoiceField(choices=GOAL_CHOICES, required=True)
    calories_target = serializers.IntegerField(required=True, validators=[MinValueValidator(1)])
    meals_count = serializers.IntegerField(required=True, validators=[MinValueValidator(1), MaxValueValidator(6)])
    dietary_restrictions = serializers.ListField(child=serializers.CharField(max_length=100), required=False, allow_empty=True)
    preferred_cuisine = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_goal(self, value):
        valid_goals = [choice[0] for choice in GOAL_CHOICES]
        if value.lower() not in valid_goals:
            raise serializers.ValidationError(f"Objetivo inválido. Opções válidas: {', '.join(valid_goals)}")
        return value

class SuggestedMealSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    type = serializers.SerializerMethodField()  # Mapeia para Diet.meal
    description = serializers.CharField(required=False, allow_blank=True)
    calories = serializers.FloatField()
    protein = serializers.FloatField()
    carbs = serializers.FloatField()
    fat = serializers.FloatField()
    ingredients = serializers.JSONField(required=False)
    preparation_time_minutes = serializers.IntegerField(required=False, min_value=0, allow_null=True)

    def get_type(self, obj):
        return obj.meal

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['name'] = instance.name if instance.name else f"Refeição {instance.get_meal_display()}"
        rep['description'] = instance.description if instance.description else f"Uma refeição de {instance.calories} kcal para {instance.get_meal_display()}."
        return rep

class DailyDietPlanSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.IntegerField(read_only=True)
    date = serializers.DateField()
    target_calories = serializers.FloatField(required=False, allow_null=True)
    target_protein = serializers.FloatField(required=False, allow_null=True)
    target_carbs = serializers.FloatField(required=False, allow_null=True)
    target_fat = serializers.FloatField(required=False, allow_null=True)
    water_intake_ml = serializers.IntegerField(required=False, min_value=0, allow_null=True)
    suggested_meals = SuggestedMealSerializer(many=True)
    macro_distribution_percentage = serializers.JSONField(required=False)
    rating = serializers.FloatField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        raise NotImplementedError("Não suporta criação direta.")

    def update(self, instance, validated_data):
        raise NotImplementedError("Não suporta atualização direta.")
