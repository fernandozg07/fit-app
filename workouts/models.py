from django.db import models
from django.conf import settings

class Workout(models.Model):
    WORKOUT_TYPES = [
        ('cardio', 'Cardio'),
        ('musculacao', 'Musculação'),
        ('flexibilidade', 'Flexibilidade'),
    ]

    INTENSITY_LEVELS = [
        ('Baixa', 'Baixa'),
        ('Moderada', 'Moderada'),
        ('Alta', 'Alta'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workout_type = models.CharField(max_length=30, choices=WORKOUT_TYPES)
    intensity = models.CharField(max_length=10, choices=INTENSITY_LEVELS)
    duration = models.DurationField()
    exercises = models.TextField()
    series_reps = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100)
    carga = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.workout_type} ({self.user.email})"


class WorkoutLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    duration = models.DurationField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.workout.workout_type} em {self.date.date()}"


class WorkoutFeedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    rating = models.IntegerField()
    feedback_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - Nota: {self.rating} ({self.workout.workout_type})"
