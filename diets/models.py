from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

def validate_positive(value):
    if value < 0:
        raise ValidationError(f'O valor {value} deve ser positivo.')

MEAL_CHOICES = [
    ('breakfast', 'Café da manhã'),
    ('lunch', 'Almoço'),
    ('dinner', 'Jantar'),
    ('snack', 'Lanche'),
    ('afternoon_snack', 'Lanche da Tarde'),
]

class Diet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="diets")
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
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_meal_display()} - {self.user.email} ({self.date})"

class DietFeedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    diet = models.ForeignKey(Diet, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Feedback de Dieta"
        verbose_name_plural = "Feedbacks de Dieta"
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback de {self.user.email} - Nota {self.rating}"
