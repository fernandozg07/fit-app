from rest_framework import serializers
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'user', 'user_message', 'bot_response', 'timestamp']
        read_only_fields = ['id', 'user', 'bot_response', 'timestamp']
