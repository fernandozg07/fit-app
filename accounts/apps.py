from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from django.contrib.auth import get_user_model
        from django.db.utils import OperationalError
        from django.db import ProgrammingError
        try:
            User = get_user_model()
            if not User.objects.filter(email="fernandozaninigalletti@gmail.com").exists():
                User.objects.create_superuser(
                    email="fernandozaninigalletti@gmail.com",
                    password="fg020607"
                )
                print("✔️ Superusuário criado automaticamente.")
        except (OperationalError, ProgrammingError):
            # Ignora erro se o banco de dados ainda não estiver pronto
            pass
