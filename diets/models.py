from django.db import models
from django.conf import settings
from accounts.models import User
from django.core.exceptions import ValidationError

# Função de validação para valores positivos
def validate_positive(value):
    if value < 0:
        raise ValidationError(f'O valor {value} deve ser positivo.')

MEAL_CHOICES = [
    ('breakfast', 'Café da manhã'),
    ('lunch', 'Almoço'),
    ('dinner', 'Jantar'),
    ('snack', 'Lanche'),
    ('afternoon_snack', 'Lanche da Tarde')
]

class Diet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="diets")
    meal = models.CharField(max_length=20, choices=MEAL_CHOICES)
    calories = models.FloatField(validators=[validate_positive])
    protein = models.FloatField(validators=[validate_positive])
    carbs = models.FloatField(validators=[validate_positive])
    fat = models.FloatField(validators=[validate_positive])
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dieta"
        verbose_name_plural = "Dietas"

    def __str__(self):
        return f"{self.meal.capitalize()} - {self.user.email} ({self.date})"


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    workout_type = models.CharField(max_length=50)
    intensity = models.CharField(max_length=20)
    duration = models.DurationField()
    exercises = models.TextField()
    series_reps = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=50)
    carga = models.FloatField(validators=[validate_positive], default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Treino"
        verbose_name_plural = "Treinos"

    def __str__(self):
        return f"Treino de {self.workout_type} - {self.user.email} ({self.created_at.date()})"


class DietFeedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    diet = models.ForeignKey(Diet, on_delete=models.CASCADE)
    rating = models.IntegerField()
    feedback_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback de {self.user.email} - Nota {self.rating}"
