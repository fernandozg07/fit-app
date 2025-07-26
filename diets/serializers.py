from rest_framework import serializers
from .models import Diet, DietFeedback, MEAL_CHOICES, GOAL_CHOICES # Importar GOAL_CHOICES
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class DietSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Diet.
    Inclui todos os campos do modelo para operações CRUD.
    """
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

    # O método validate foi mantido com 'pass' para permitir múltiplos registros
    # do mesmo tipo de refeição no mesmo dia, se a intenção for registrar o consumo.
    # Se a intenção for ter um plano único por dia/tipo, esta validação precisaria ser reativada.
    def validate(self, data):
        return data

class DietFeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo DietFeedback.
    """
    class Meta:
        model = DietFeedback
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("A nota (rating) deve estar entre 1 e 5.")
        return value

class DietGenerateInputSerializer(serializers.Serializer):
    """
    Serializer para validar os dados de entrada para a geração de dieta pela IA.
    """
    goal = serializers.ChoiceField(
        choices=GOAL_CHOICES, # Usar GOAL_CHOICES do models para consistência
        required=True,
        help_text="Objetivo fitness (e.g., 'perda_peso', 'ganho_muscular')."
    )
    calories_target = serializers.IntegerField(
        required=True, # Mantido como obrigatório, se for opcional, adicione allow_null=True
        validators=[MinValueValidator(1)],
        help_text="Meta de calorias diárias."
    )
    meals_count = serializers.IntegerField(
        required=True,
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        help_text="Número de refeições a serem geradas."
    )
    dietary_restrictions = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True,
        help_text="Lista de restrições dietéticas (e.g., 'vegetariano', 'sem glúten')."
    )
    preferred_cuisine = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Culinária preferida (e.g., 'mediterrânea', 'asiática')."
    )

    def validate_goal(self, value):
        valid_goals = [choice[0] for choice in GOAL_CHOICES] # Obter valores válidos de GOAL_CHOICES
        if value.lower() not in valid_goals:
            raise serializers.ValidationError(f"Objetivo inválido. Opções válidas: {', '.join(valid_goals)}")
        return value

# Serializer para formatar as refeições sugeridas dentro de um plano diário
class SuggestedMealSerializer(serializers.Serializer):
    """
    Serializer para representar uma refeição sugerida dentro do DailyDietPlan.
    Mapeia os campos do modelo Diet para a estrutura esperada pelo frontend.
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    type = serializers.ChoiceField(choices=MEAL_CHOICES) # Usar MEAL_CHOICES do models
    description = serializers.CharField(required=False, allow_blank=True)
    calories = serializers.FloatField()
    protein = serializers.FloatField()
    carbs = serializers.FloatField()
    fat = serializers.FloatField()
    ingredients = serializers.JSONField(required=False) # JSONField para lista de strings
    preparation_time_minutes = serializers.IntegerField(required=False, min_value=0, allow_null=True)

    def to_representation(self, instance):
        """
        Mapeia um objeto Diet para a estrutura de SuggestedMeal.
        """
        representation = super().to_representation(instance)
        # Garante que os campos do modelo Diet sejam mapeados corretamente
        representation['id'] = instance.id
        representation['name'] = instance.name if instance.name else f"Refeição {instance.get_meal_display()}"
        representation['type'] = instance.meal
        representation['description'] = instance.description if instance.description else f"Uma refeição de {instance.calories} kcal para {instance.get_meal_display()}."
        representation['ingredients'] = instance.ingredients # Já é um JSONField, então deve ser uma lista
        representation['preparation_time_minutes'] = instance.preparation_time_minutes
        return representation

# Serializer para o plano de dieta diário agregado (não baseado em modelo)
class DailyDietPlanSerializer(serializers.Serializer):
    """
    Serializer para representar um plano de dieta diário agregado.
    Não corresponde diretamente a um modelo persistente, mas sim a uma agregação de dados.
    """
    id = serializers.IntegerField(read_only=True, help_text="ID do plano diário (pode ser o ID do primeiro Diet do dia ou gerado).")
    user = serializers.IntegerField(read_only=True)
    date = serializers.DateField(help_text="Data do plano diário.")
    target_calories = serializers.FloatField(help_text="Meta de calorias para o dia.")
    target_protein = serializers.FloatField(help_text="Meta de proteína para o dia em gramas.")
    target_carbs = serializers.FloatField(help_text="Meta de carboidratos para o dia em gramas.")
    target_fat = serializers.FloatField(help_text="Meta de gordura para o dia em gramas.")
    water_intake_ml = serializers.IntegerField(required=False, min_value=0, allow_null=True, help_text="Meta de consumo de água para o dia em mililitros.")
    suggested_meals = SuggestedMealSerializer(many=True, help_text="Lista de refeições sugeridas para o dia.")
    macro_distribution_percentage = serializers.JSONField(required=False, help_text="Distribuição percentual de macronutrientes.")
    rating = serializers.FloatField(required=False, allow_null=True, help_text="Avaliação média do plano diário, se houver.")
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    # Métodos create e update não implementados, pois este Serializer não persiste um modelo diretamente.
    def create(self, validated_data):
        raise NotImplementedError("DailyDietPlanSerializer does not support direct creation.")

    def update(self, instance, validated_data):
        raise NotImplementedError("DailyDietPlanSerializer does not support direct updates.")
