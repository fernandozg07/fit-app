from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            raise ValueError("A senha é obrigatória.")
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('is_staff') or not extra_fields.get('is_superuser'):
            raise ValueError('Superusuário precisa ter is_staff=True e is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    # <--- ATUALIZADO: FITNESS_GOALS para corresponder ao frontend
    FITNESS_GOALS = [
        ('perda_peso', 'Perda de peso'),
        ('ganho_muscular', 'Ganho de massa muscular'),
        ('manutencao', 'Manutenção'), # <--- CORRIGIDO
        ('resistencia', 'Resistência'), # <--- CORRIGIDO
    ]
    
    # <--- ADICIONADO: ACTIVITY_LEVELS
    ACTIVITY_LEVELS = [
        ('sedentary', 'Sedentário'),
        ('lightly_active', 'Levemente ativo'),
        ('moderately_active', 'Moderadamente ativo'),
        ('very_active', 'Muito ativo'),
        ('extremely_active', 'Extremamente ativo'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    fitness_goal = models.CharField(max_length=50, choices=FITNESS_GOALS, null=True, blank=True)
    dietary_restrictions = models.TextField(null=True, blank=True)
    activity_level = models.CharField(max_length=50, choices=ACTIVITY_LEVELS, null=True, blank=True) # <--- ADICIONADO

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
