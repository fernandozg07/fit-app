from django.db import models
from django.conf import settings
from accounts.models import User


class Workout(models.Model):
    WORKOUT_TYPES = [
        ('cardio', 'Cardio'),
        ('musculacao', 'Musculação'),
        ('flexibilidade', 'Flexibilidade'),
    ]

    INTENSITY_LEVELS = [
        ('baixa', 'Baixa'),
        ('moderada', 'Moderada'),
        ('alta', 'Alta'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workout_type = models.CharField(max_length=30, choices=WORKOUT_TYPES, default='musculacao')
    intensity = models.CharField(max_length=10, choices=INTENSITY_LEVELS, default='moderada')
    duration = models.DurationField()
    exercises = models.TextField(blank=True)
    series_reps = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    carga = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.workout_type} ({self.user.email}) - {self.duration}"


class WorkoutLog(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    nota = models.IntegerField()
    duracao = models.IntegerField()  # duração real do treino realizado (em minutos)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log - {self.workout} ({self.created_at.date()})"


class WorkoutFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout_log = models.ForeignKey('WorkoutLog', on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField()
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.email} on {self.workout_log}"
