from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_message', 'bot_response', 'timestamp')
    search_fields = ('user__email', 'user_message', 'bot_response')
    list_filter = ('timestamp',)
