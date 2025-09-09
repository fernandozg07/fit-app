from django.db import models
from django.conf import settings

class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_messages")
    user_message = models.TextField(verbose_name="Mensagem do Usuário")
    bot_response = models.TextField(verbose_name="Resposta da IA")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Mensagem de Chat"
        verbose_name_plural = "Mensagens de Chat"

    def __str__(self):
        return f'{self.user.email} - {self.user_message[:30]}'
