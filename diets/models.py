from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone # Importar timezone para default da data

# Validador para garantir que valores numéricos sejam positivos
def validate_positive(value):
    if value < 0:
        raise ValidationError(f'O valor {value} deve ser positivo.')

# Opções de tipos de refeição (expandido para consistência com o frontend)
MEAL_CHOICES = [
    ('breakfast', 'Café da manhã'),
    ('lunch', 'Almoço'),
    ('dinner', 'Jantar'),
    ('snack', 'Lanche'),
    ('afternoon_snack', 'Lanche da Tarde'),
    ('pre_workout', 'Pré-treino'),
    ('post_workout', 'Pós-treino'),
]

# Opções de objetivos de dieta (expandido para consistência com o frontend)
GOAL_CHOICES = [
    ('perda_peso', 'Perda de peso'),
    ('ganho_muscular', 'Ganho de massa muscular'),
    ('manutencao', 'Manutenção'),
    ('resistencia', 'Resistência'), 
]

class Diet(models.Model):
    """
    Representa uma refeição individual ou uma entrada em um plano de dieta.
    Este modelo também armazena os parâmetros da solicitação de geração de dieta
    para que cada refeição gerada tenha o contexto do plano ao qual pertence.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="diets")
    meal = models.CharField(max_length=20, choices=MEAL_CHOICES, help_text="Tipo de refeição (e.g., café da manhã, almoço).")
    
    # Detalhes nutricionais da refeição
    calories = models.FloatField(validators=[MinValueValidator(0.0)], help_text="Calorias da refeição.")
    protein = models.FloatField(validators=[MinValueValidator(0.0)], help_text="Proteína em gramas.")
    carbs = models.FloatField(validators=[MinValueValidator(0.0)], help_text="Carboidratos em gramas.")
    fat = models.FloatField(validators=[MinValueValidator(0.0)], help_text="Gordura em gramas.")
    
    date = models.DateField(auto_now_add=True, help_text="Data em que a refeição foi criada/sugerida.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Campos adicionais para enriquecer a descrição da refeição (para SuggestedMealSerializer)
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Nome da refeição (e.g., 'Omelete de Vegetais').")
    description = models.TextField(blank=True, null=True, help_text="Descrição detalhada da refeição.")
    ingredients = models.JSONField(default=list, blank=True, help_text="Lista de ingredientes em formato JSON.")
    preparation_time_minutes = models.IntegerField(
        blank=True, null=True, validators=[MinValueValidator(0)],
        help_text="Tempo de preparo estimado em minutos."
    )
    
    # Campos da solicitação de geração de dieta (para contexto do plano)
    goal = models.CharField(
        max_length=50, choices=GOAL_CHOICES, blank=True, null=True,
        help_text="Objetivo fitness principal para o plano de dieta."
    )
    dietary_restrictions = models.JSONField(
        default=list, blank=True,
        help_text="Restrições dietéticas (e.g., 'vegetariano', 'sem glúten') em formato JSON."
    )
    preferred_cuisine = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Tipo de culinária preferida (e.g., 'mediterrânea', 'asiática')."
    )
    
    # Metas nutricionais diárias (armazenadas por refeição para agregação no frontend/views)
    target_calories = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0)], help_text="Meta de calorias diárias para o plano.")
    target_protein = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0)], help_text="Meta de proteína diária em gramas.")
    target_carbs = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0)], help_text="Meta de carboidratos diária em gramas.")
    target_fat = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0)], help_text="Meta de gordura diária em gramas.")
    water_intake_ml = models.IntegerField(
        blank=True, null=True, validators=[MinValueValidator(0)],
        help_text="Meta de consumo de água diário em mililitros."
    )
    
    # Rating para a refeição ou plano (se aplicável, pode ser um campo calculado ou armazenado)
    rating = models.FloatField(
        blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Avaliação da refeição ou do plano de dieta (1-5)."
    )

    class Meta:
        verbose_name = "Dieta"
        verbose_name_plural = "Dietas"
        ordering = ['-date', 'meal'] # Ordena por data decrescente e depois por tipo de refeição

    def __str__(self):
        return f"{self.get_meal_display()} - {self.user.email} ({self.date})"

class DietFeedback(models.Model):
    """
    Registra o feedback do usuário sobre uma refeição específica.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    diet = models.ForeignKey(Diet, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Avaliação (1-5 estrelas).")
    feedback_text = models.TextField(blank=True, help_text="Comentários adicionais do usuário.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Feedback de Dieta"
        verbose_name_plural = "Feedbacks de Dieta"
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback de {self.user.email} - Nota {self.rating}"

class ConsumedMealLog(models.Model):
    """
    Representa o registro de uma refeição REALMENTE CONSUMIDA pelo usuário.
    Isso é diferente de um plano de dieta sugerido (Diet).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consumed_meals")
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES, help_text="Tipo de refeição consumida.")
    food_items = models.TextField(help_text="Descrição dos itens alimentares consumidos (e.g., '2 ovos, 1 fatia de pão').")
    calories_consumed = models.FloatField(validators=[MinValueValidator(0.0)], help_text="Calorias consumidas.")
    protein_consumed = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0)], help_text="Proteína consumida em gramas.")
    carbs_consumed = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0)], help_text="Carboidratos consumidos em gramas.")
    fat_consumed = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0)], help_text="Gordura consumida em gramas.")
    date = models.DateField(default=timezone.now, help_text="Data em que a refeição foi consumida.")
    time = models.TimeField(null=True, blank=True, help_text="Hora em que a refeição foi consumida.")
    notes = models.TextField(blank=True, null=True, help_text="Notas adicionais sobre a refeição consumida.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Refeição Consumida"
        verbose_name_plural = "Refeições Consumidas"
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.user.email} - {self.get_meal_type_display()} ({self.date})"
