# accounts/apps.py

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Registra o sinal post_migrate para criar o superusuário depois das migrações
        post_migrate.connect(create_superuser_if_needed, sender=self)


# Função que será chamada após as migrações
def create_superuser_if_needed(sender, **kwargs):
    try:
        User = get_user_model()
        # Verifica se o superusuário já existe
        if not User.objects.filter(email="fernandozaninigalletti@gmail.com").exists():
            # Cria o superusuário se não existir
            User.objects.create_superuser(
                email="fernandozaninigalletti@gmail.com",
                password="fg020607"
            )
            print("✔️ Superusuário criado automaticamente.")
    except (OperationalError, ProgrammingError):
        # Ignora erro se o banco de dados ainda não estiver pronto
        pass
