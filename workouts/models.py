# workouts/models.py
from django.db import models
from django.conf import settings
from datetime import timedelta
from django.core.validators import MinValueValidator, MaxValueValidator 

# Definições de CHOICES movidas para o nível superior do módulo
WORKOUT_TYPES = [
    ('cardio', 'Cardio'),
    ('musculacao', 'Musculação'),
    ('flexibilidade', 'Flexibilidade'),
    ('yoga', 'Yoga'), 
    ('strength', 'Força'), 
    ('hiit', 'HIIT'), 
]

INTENSITY_LEVELS = [
    ('baixa', 'Baixa'),
    ('moderada', 'Moderada'),
    ('alta', 'Alta'),
]

# FOCUS_CHOICES movido para fora da classe Workout
FOCUS_CHOICES = [
    ('fullbody', 'Corpo Inteiro'),
    ('upper_body', 'Membros Superiores'),
    ('lower_body', 'Membros Inferiores'),
    ('core', 'Core'),
    ('cardio', 'Cardio'), 
    ('flexibility', 'Flexibilidade'), 
    ('custom', 'Personalizado'), 
]

DIFFICULTY_CHOICES = [
    ('iniciante', 'Iniciante'),
    ('intermediario', 'Intermediário'),
    ('avancado', 'Avançado'),
]

STATUS_CHOICES = [
    ('pending', 'Pendente'),
    ('completed', 'Concluído'),
    ('skipped', 'Pulado'),
    ('recommended', 'Recomendado'), 
    ('archived', 'Arquivado'), 
]

class Workout(models.Model):
    """
    Modelo para representar um treino personalizado.
    Armazena detalhes do treino, incluindo tipo, intensidade, duração,
    exercícios (como JSON), foco, grupos musculares, equipamentos, etc.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text="Usuário ao qual o treino pertence.")
    workout_type = models.CharField(max_length=30, choices=WORKOUT_TYPES, default='musculacao', help_text="Tipo geral do treino (e.g., Musculação, Cardio).")
    intensity = models.CharField(max_length=10, choices=INTENSITY_LEVELS, default='moderada', help_text="Nível de intensidade do treino.")
    duration = models.DurationField(help_text="Duração planejada do treino (timedelta).") 
    exercises = models.TextField(blank=True, help_text="Detalhes dos exercícios em formato JSON string (lista de objetos).")
    series_reps = models.CharField(max_length=100, blank=True, help_text="Séries e repetições padrão para o treino (ex: '3x12').")
    frequency = models.CharField(max_length=100, blank=True, help_text="Frequência recomendada para o treino (ex: '3x por semana').")
    carga = models.PositiveIntegerField(default=0, help_text="Carga padrão em kg (se aplicável, pode ser 0 para peso corporal).")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data e hora de criação do treino.")
    
    # Campo 'focus' agora usa as escolhas definidas globalmente
    focus = models.CharField(max_length=50, choices=FOCUS_CHOICES, default='fullbody', help_text="Foco principal do treino (e.g., Membros Superiores, Corpo Inteiro).") 
    
    # Campos JSONField para armazenar listas de strings
    muscle_groups = models.JSONField(default=list, blank=True, help_text="Lista de grupos musculares alvo específicos (e.g., ['Tríceps', 'Bíceps']).")
    equipment = models.JSONField(default=list, blank=True, help_text="Lista de equipamentos necessários (e.g., ['Halteres', 'Barra']).")
    
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Nome gerado ou customizado para o treino.")
    description = models.TextField(blank=True, null=True, help_text="Descrição detalhada do treino.")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='iniciante', help_text="Nível de dificuldade do treino.")
    
    rating = models.FloatField(
        blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Avaliação média do treino (1-5 estrelas)."
    )
    completed_date = models.DateField(blank=True, null=True, help_text="Data em que o treino foi concluído pela última vez.")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', help_text="Status atual do treino (pendente, concluído, etc.).")
    updated_at = models.DateTimeField(auto_now=True, help_text="Data e hora da última atualização do treino.")

    class Meta:
        verbose_name = "Treino"
        verbose_name_plural = "Treinos"
        ordering = ['-created_at'] # Ordena por data de criação decrescente

    def __str__(self):
        return f"{self.name or self.get_workout_type_display()} ({self.user.email}) - {self.get_difficulty_display()}"

class WorkoutLog(models.Model):
    """
    Registra cada vez que um treino é realizado, com nota e duração.
    """
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='logs', help_text="Treino ao qual este log se refere.")
    nota = models.IntegerField(help_text="Nota/avaliação do treino realizado (1-5).")
    duracao = models.IntegerField(help_text="Duração real do treino em minutos.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data e hora do registro do log.")

    class Meta:
        verbose_name = "Log de Treino"
        verbose_name_plural = "Logs de Treino"
        ordering = ['-created_at']

    def __str__(self):
        return f"Log de {self.workout.name or self.workout.workout_type} ({self.created_at.date()}) - Nota: {self.nota}"

class WorkoutFeedback(models.Model):
    """
    Registra feedback mais detalhado sobre um treino específico (opcionalmente ligado a um log).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text="Usuário que forneceu o feedback.")
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True, help_text="Treino avaliado.")
    workout_log = models.ForeignKey(WorkoutLog, on_delete=models.CASCADE, null=True, blank=True, help_text="Log de treino associado (opcional).")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Avaliação do treino (1-5 estrelas).")
    comments = models.TextField(blank=True, null=True, help_text="Comentários adicionais do usuário sobre o treino.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data e hora do feedback.")

    class Meta:
        verbose_name = "Feedback de Treino"
        verbose_name_plural = "Feedbacks de Treino"
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback de {self.user.email} (Treino: {self.workout.name if self.workout else 'N/A'}) - Nota: {self.rating}"
