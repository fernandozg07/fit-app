from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

def validate_positive(value):
    if value < 0:
        raise ValidationError(f'O valor {value} deve ser positivo.')

MEAL_CHOICES = [
    ('breakfast', 'Café da manhã'),
    ('lunch', 'Almoço'),
    ('dinner', 'Jantar'),
    ('snack', 'Lanche'),
    ('afternoon_snack', 'Lanche da Tarde'),
    ('pre_workout', 'Pré-treino'),
    ('post_workout', 'Pós-treino'),
]

GOAL_CHOICES = [
    ('perda_peso', 'Perda de peso'),
    ('ganho_muscular', 'Ganho de massa muscular'),
    ('manutencao', 'Manutenção'),
    ('resistencia', 'Resistência'), 
]

class Diet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="diets")
    meal = models.CharField(max_length=20, choices=MEAL_CHOICES, help_text="Tipo de refeição.")
    
    calories = models.FloatField(validators=[MinValueValidator(0.0)], help_text="Calorias da refeição.")
    protein = models.FloatField(validators=[MinValueValidator(0.0)], help_text="Proteína em gramas.")
    carbs = models.FloatField(validators=[MinValueValidator(0.0)], help_text="Carboidratos em gramas.")
    fat = models.FloatField(validators=[MinValueValidator(0.0)], help_text="Gordura em gramas.")
    
    date = models.DateField(auto_now_add=True, help_text="Data da criação/sugestão da refeição.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Campos adicionais (usados no serializer SuggestedMealSerializer)
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Nome da refeição.")
    description = models.TextField(blank=True, null=True, help_text="Descrição detalhada da refeição.")
    ingredients = models.JSONField(default=list, blank=True, help_text="Lista de ingredientes em JSON.")
    preparation_time_minutes = models.PositiveIntegerField(blank=True, null=True, help_text="Tempo de preparo em minutos.")

    # Contexto da geração da dieta
    goal = models.CharField(max_length=50, choices=GOAL_CHOICES, blank=True, null=True, help_text="Objetivo do plano.")
    dietary_restrictions = models.JSONField(default=list, blank=True, help_text="Restrições alimentares em JSON.")
    preferred_cuisine = models.CharField(max_length=100, blank=True, null=True, help_text="Culinária preferida.")

    # Metas diárias armazenadas para agregação
    target_calories = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0)], help_text="Meta diária de calorias.")
    target_protein = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0)], help_text="Meta diária de proteína (g).")
    target_carbs = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0)], help_text="Meta diária de carboidratos (g).")
    target_fat = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0)], help_text="Meta diária de gordura (g).")
    water_intake_ml = models.PositiveIntegerField(blank=True, null=True, help_text="Meta diária de água (ml).")

    rating = models.FloatField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Avaliação (1-5).")

    class Meta:
        verbose_name = "Dieta"
        verbose_name_plural = "Dietas"
        ordering = ['-date', 'meal']

    def __str__(self):
        return f"{self.get_meal_display()} - {self.user.email} ({self.date})"


class DietFeedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    diet = models.ForeignKey(Diet, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Avaliação (1-5 estrelas).")
    feedback_text = models.TextField(blank=True, null=True, help_text="Comentário adicional.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Feedback de Dieta"
        verbose_name_plural = "Feedbacks de Dieta"
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback de {self.user.email} - Nota {self.rating}"


class ConsumedMealLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consumed_meals")
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES, help_text="Tipo de refeição consumida.")
    food_items = models.TextField(help_text="Descrição dos alimentos consumidos.")
    
    calories_consumed = models.FloatField(validators=[MinValueValidator(0.0)], help_text="Calorias consumidas.")
    protein_consumed = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0)], help_text="Proteína consumida (g).")
    carbs_consumed = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0)], help_text="Carboidratos consumidos (g).")
    fat_consumed = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0)], help_text="Gordura consumida (g).")

    date = models.DateField(default=timezone.now, help_text="Data da refeição consumida.")
    time = models.TimeField(blank=True, null=True, help_text="Hora da refeição consumida.")
    notes = models.TextField(blank=True, null=True, help_text="Notas adicionais sobre a refeição.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Refeição Consumida"
        verbose_name_plural = "Refeições Consumidas"
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.user.email} - {self.get_meal_type_display()} ({self.date})"
