from django.db import models
from accounts.models import User

class ProgressEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.FloatField()
    body_fat = models.FloatField(null=True, blank=True)  # <-- esse campo deve existir
    muscle_mass = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.date}"
