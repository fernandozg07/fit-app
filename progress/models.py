from django.db import models
from accounts.models import User # Importe o modelo User corretamente

class ProgressEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(help_text="Data do registro de progresso.")
    weight = models.FloatField(help_text="Peso em quilogramas (kg).")
    body_fat = models.FloatField(null=True, blank=True, help_text="Percentual de gordura corporal (%).")
    muscle_mass = models.FloatField(null=True, blank=True, help_text="Massa muscular em quilogramas (kg).")
    notes = models.TextField(blank=True, null=True, verbose_name="Observações", help_text="Notas adicionais sobre o progresso.")

    # NOVOS CAMPOS ADICIONADOS PARA CONSISTÊNCIA COM O FRONTEND (se aplicável)
    # Se o frontend enviar esses campos, eles devem estar aqui.
    arm_circumference = models.FloatField(null=True, blank=True, help_text="Circunferência do braço em cm.")
    chest_circumference = models.FloatField(null=True, blank=True, help_text="Circunferência do peito em cm.")
    waist_circumference = models.FloatField(null=True, blank=True, help_text="Circunferência da cintura em cm.")
    hip_circumference = models.FloatField(null=True, blank=True, help_text="Circunferência do quadril em cm.")
    thigh_circumference = models.FloatField(null=True, blank=True, help_text="Circunferência da coxa em cm.")
    calf_circumference = models.FloatField(null=True, blank=True, help_text="Circunferência da panturrilha em cm.")
    photo_url_before = models.URLField(max_length=500, null=True, blank=True, help_text="URL da foto 'antes'.")
    photo_url_after = models.URLField(max_length=500, null=True, blank=True, help_text="URL da foto 'depois'.")

    # Campos de data/hora de criação e atualização
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data e hora de criação do registro.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Data e hora da última atualização do registro.")


    class Meta:
        verbose_name = "Progresso"
        verbose_name_plural = "Progresso"
        ordering = ['-date'] # Ordena por data decrescente (mais recente primeiro)
        unique_together = ['user', 'date'] # Garante apenas um registro por usuário por dia

    def __str__(self):
        return f"{self.user.email} - {self.date}"