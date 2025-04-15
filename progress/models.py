from django.db import models
from accounts.models import User

class ProgressEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.FloatField()
    body_fat = models.FloatField(null=True, blank=True)
    muscle_mass = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Progresso"
        verbose_name_plural = "Progresso"
        ordering = ['-date']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.email} - {self.date}"
