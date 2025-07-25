from rest_framework import serializers
from .models import Diet, DietFeedback, MEAL_CHOICES
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class DietSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diet
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, data):
        # A validação de unicidade por refeição/data/usuário deve ser feita aqui
        # apenas se você não quiser que o usuário registre a mesma "meal" no mesmo "date"
        # Se a intenção é que o usuário possa registrar múltiplas "breakfasts" no mesmo dia,
        # essa validação precisaria de um campo mais granular (ex: timestamp) ou ser removida.
        # Por enquanto, mantemos para evitar duplicação exata de "meal type" no mesmo dia.
        user = self.context.get('request').user if 'request' in self.context else None
        meal = data.get('meal')
        date = data.get('date', timezone.now().date())

        if user and Diet.objects.filter(user=user, meal=meal, date=date).exists():
            # Removido para permitir múltiplos registros de refeições do mesmo tipo no mesmo dia,
            # se a intenção for registrar o que foi *consumido* e não apenas um "plano" único.
            # Se você quer um plano único por dia/tipo, reative esta linha:
            # raise serializers.ValidationError("Essa refeição já foi registrada hoje para este tipo.")
            pass # Permite múltiplas entradas do mesmo tipo de refeição no mesmo dia para fins de registro

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

class DietGenerateInputSerializer(serializers.Serializer):
    # CORRIGIDO: Valores literais para o goal, conforme esperado pelo backend
    goal = serializers.ChoiceField(choices=['perda de peso', 'ganho de massa muscular', 'manutenção'], required=True)
    calories_target = serializers.IntegerField(required=True, validators=[MinValueValidator(1)])
    meals_count = serializers.IntegerField(required=True, validators=[MinValueValidator(1), MaxValueValidator(6)])
    dietary_restrictions = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True
    )
    preferred_cuisine = serializers.CharField(max_length=100, required=False, allow_blank=True) # Adicionado

    def validate_goal(self, value):
        valid_goals = ['perda de peso', 'ganho de massa muscular', 'manutenção']
        if value.lower() not in valid_goals:
            raise serializers.ValidationError(f"Objetivo inválido. Opções válidas: {', '.join(valid_goals)}")
        return value

# NOVO SERIALIZER PARA AS REFEIÇÕES SUGERIDAS DENTRO DO DAILYDIETPLAN
class SuggestedMealSerializer(serializers.Serializer):
    # As chaves aqui devem corresponder aos campos do modelo Diet que você quer expor
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True) # Adicionado, pois Diet não tem 'name'
    type = serializers.ChoiceField(choices=MEAL_CHOICES) # Usar MEAL_CHOICES do models
    description = serializers.CharField(required=False, allow_blank=True) # Adicionado, pois Diet não tem 'description'
    calories = serializers.FloatField()
    protein = serializers.FloatField()
    carbs = serializers.FloatField()
    fat = serializers.FloatField()
    ingredients = serializers.CharField(required=False, allow_blank=True) # Assumindo que é uma string
    preparation_time_minutes = serializers.IntegerField(required=False, min_value=0) # Adicionado

    # Método para mapear um objeto Diet para a estrutura de SuggestedMeal
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Mapeia os campos do Diet para os campos esperados pelo SuggestedMeal
        representation['name'] = f"Refeição {instance.get_meal_display()}" # Nome genérico ou mais específico
        representation['type'] = instance.meal
        representation['description'] = f"Uma refeição de {instance.calories} kcal para {instance.get_meal_display()}." # Descrição genérica
        representation['ingredients'] = "Ingredientes não especificados." # Placeholder
        representation['preparation_time_minutes'] = 30 # Placeholder
        return representation

# NOVO SERIALIZER PARA O DAILYDIETPLAN
class DailyDietPlanSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True) # Um ID para o plano diário (pode ser o ID do primeiro Diet do dia ou gerado)
    user = serializers.IntegerField(read_only=True)
    date = serializers.DateField()
    target_calories = serializers.FloatField()
    target_protein = serializers.FloatField()
    target_carbs = serializers.FloatField()
    target_fat = serializers.FloatField()
    water_intake_ml = serializers.IntegerField(required=False, min_value=0) # Opcional
    suggested_meals = SuggestedMealSerializer(many=True) # Lista de refeições sugeridas
    macro_distribution_percentage = serializers.JSONField(required=False) # Armazena como JSON
    rating = serializers.FloatField(required=False) # Rating médio do dia, se houver
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    # Este método `create` é fictício para o Serializer, pois não há um modelo `DailyDietPlan` direto.
    # A lógica de criação real será no view.
    def create(self, validated_data):
        raise NotImplementedError("DailyDietPlanSerializer does not support direct creation.")

    def update(self, instance, validated_data):
        raise NotImplementedError("DailyDietPlanSerializer does not support direct updates.")
