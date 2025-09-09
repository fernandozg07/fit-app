from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Cria ou atualiza um superusuário com email e senha padrão"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        email = "fernandozaninigalletti@gmail.com"
        password = "fg020607"

        # Tenta criar ou obter o usuário
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "is_staff": True,
                "is_superuser": True,
            }
        )

        # Define a senha
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        # Verifica se o superusuário foi criado ou se já existia
        if created:
            self.stdout.write(self.style.SUCCESS("Superusuário criado com sucesso."))  # Removido o "✅" para evitar problemas de codificação
        else:
            self.stdout.write(self.style.WARNING("Superusuário já existia. Dados atualizados."))  # Removido o "⚠️" para evitar problemas de codificação
