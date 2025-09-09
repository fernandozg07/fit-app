from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    """
    Gerenciador de modelos personalizado para o modelo de usuário.
    Define métodos para criar usuários e superusuários.
    """
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
    """
    Modelo de usuário personalizado para o aplicativo Fitness API.
    Utiliza o email como campo de nome de usuário.
    """
    # Opções para o objetivo de fitness
    FITNESS_GOALS = [
        ('perda_peso', 'Perda de peso'),
        ('ganho_muscular', 'Ganho de massa muscular'),
        ('manutencao', 'Manutenção'), 
        ('resistencia', 'Resistência'), 
    ]
    
    # Opções para o nível de atividade
    ACTIVITY_LEVELS = [
        ('sedentary', 'Sedentário'),
        ('lightly_active', 'Levemente ativo'),
        ('moderately_active', 'Moderadamente ativo'), # CORRIGIDO: Removido o parêntese extra
        ('very_active', 'Muito ativo'),
        ('extremely_active', 'Extremamente ativo'),
    ]

    # Opções para o gênero
    GENDER_CHOICES = [
        ('male', 'Masculino'),
        ('female', 'Feminino'),
        ('other', 'Outro'),
    ]

    email = models.EmailField(unique=True, help_text="Endereço de e-mail único do usuário.")
    first_name = models.CharField(max_length=150, blank=True, help_text="Primeiro nome do usuário.")
    last_name = models.CharField(max_length=150, blank=True, help_text="Sobrenome do usuário.")
    birth_date = models.DateField(null=True, blank=True, help_text="Data de nascimento do usuário.")
    weight = models.FloatField(null=True, blank=True, help_text="Peso atual do usuário em kg.")
    height = models.FloatField(null=True, blank=True, help_text="Altura atual do usuário em cm.")
    fitness_goal = models.CharField(max_length=50, choices=FITNESS_GOALS, null=True, blank=True, help_text="Objetivo de fitness do usuário.")
    dietary_restrictions = models.TextField(null=True, blank=True, help_text="Restrições dietéticas do usuário (ex: 'vegetariano', 'sem glúten').")
    activity_level = models.CharField(max_length=50, choices=ACTIVITY_LEVELS, null=True, blank=True, help_text="Nível de atividade física do usuário.")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True, help_text="Gênero do usuário.")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
