from django.db import models
from django.conf import settings
from datetime import timedelta
from django.core.validators import MinValueValidator, MaxValueValidator # Importar validadores

class Workout(models.Model):
    WORKOUT_TYPES = [
        ('cardio', 'Cardio'),
        ('musculacao', 'Musculação'),
        ('flexibilidade', 'Flexibilidade'),
        ('yoga', 'Yoga'),
    ]

    INTENSITY_LEVELS = [
        ('baixa', 'Baixa'),
        ('moderada', 'Moderada'),
        ('alta', 'Alta'),
    ]

    FOCUS_CHOICES = [
        ('fullbody', 'Full Body'),
        ('superior', 'Membros Superiores'),
        ('inferior', 'Membros Inferiores'),
        ('core', 'Core'),
    ]

    DIFFICULTY_CHOICES = [ # Adicionado para consistência com o frontend
        ('iniciante', 'Iniciante'),
        ('moderado', 'Moderado'),
        ('avancado', 'Avançado'),
    ]

    STATUS_CHOICES = [ # Adicionado para consistência com o frontend
        ('pending', 'Pendente'),
        ('completed', 'Concluído'),
        ('skipped', 'Pulado'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workout_type = models.CharField(max_length=30, choices=WORKOUT_TYPES, default='musculacao')
    intensity = models.CharField(max_length=10, choices=INTENSITY_LEVELS, default='moderada')
    duration = models.DurationField(help_text="Duração do treino (timedelta).")
    exercises = models.TextField(blank=True, help_text="Detalhes dos exercícios em formato JSON string.")
    series_reps = models.CharField(max_length=100, blank=True, help_text="Séries e repetições padrão (ex: '3x12').")
    frequency = models.CharField(max_length=100, blank=True, help_text="Frequência recomendada (ex: '3x por semana').")
    carga = models.PositiveIntegerField(default=0, help_text="Carga padrão em kg (se aplicável).")
    created_at = models.DateTimeField(auto_now_add=True)
    focus = models.CharField(max_length=20, choices=FOCUS_CHOICES, default='fullbody', help_text="Foco principal do treino.")
    
    # NOVOS CAMPOS ADICIONADOS PARA CONSISTÊNCIA COM O FRONTEND
    muscle_groups = models.JSONField(default=list, blank=True, help_text="Grupos musculares alvo em formato JSON (lista de strings).")
    equipment = models.JSONField(default=list, blank=True, help_text="Equipamentos necessários em formato JSON (lista de strings).")
    
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Nome gerado para o treino.")
    description = models.TextField(blank=True, null=True, help_text="Descrição detalhada do treino.")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='iniciante', help_text="Nível de dificuldade do treino.")
    
    rating = models.FloatField(
        blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Avaliação média do treino (1-5 estrelas)."
    )
    completed_date = models.DateField(blank=True, null=True, help_text="Data em que o treino foi concluído pela última vez.")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', help_text="Status atual do treino (pendente, concluído, etc.).")
    updated_at = models.DateTimeField(auto_now=True) # Campo auto_now=True já existia, mas listado para clareza.

    def __str__(self):
        return f"{self.name or self.workout_type} ({self.user.email}) - {self.difficulty}"

class WorkoutLog(models.Model):
    """
    Registra cada vez que um treino é realizado, com nota e duração.
    """
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='logs')
    nota = models.IntegerField(help_text="Nota/avaliação do treino realizado (1-5).")
    duracao = models.IntegerField(help_text="Duração real do treino em minutos.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log de {self.workout.name or self.workout.workout_type} ({self.created_at.date()}) - Nota: {self.nota}"

class WorkoutFeedback(models.Model):
    """
    Registra feedback mais detalhado sobre um treino específico (opcionalmente ligado a um log).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True) # Ligado ao treino diretamente
    workout_log = models.ForeignKey(WorkoutLog, on_delete=models.CASCADE, null=True, blank=True, help_text="Log de treino associado (opcional).")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Avaliação (1-5 estrelas).")
    comments = models.TextField(blank=True, null=True, help_text="Comentários adicionais do usuário.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback de {self.user.email} (Treino: {self.workout.name if self.workout else 'N/A'}) - Nota: {self.rating}"

