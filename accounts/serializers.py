from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'first_name', 'last_name',
            'age', 'birth_date', 'weight', 'height',
            'fitness_goal', 'dietary_restrictions'
        ]
        extra_kwargs = {
            'birth_date': {'required': False, 'allow_null': True},
            'weight': {'required': False, 'allow_null': True},
            'height': {'required': False, 'allow_null': True},
            'fitness_goal': {'required': False, 'allow_null': True},
            'dietary_restrictions': {'required': False, 'allow_blank': True, 'allow_null': True},
        }

    def get_age(self, obj):
        if obj.birth_date:
            today = date.today()
            return today.year - obj.birth_date.year - (
                (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day)
            )
        return None

    def validate_weight(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("O peso deve ser um valor positivo.")
        return value

    def validate_height(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("A altura deve ser um valor positivo.")
        return value

    def validate_fitness_goal(self, value):
        valid_goals = ['perda de peso', 'ganho muscular', 'flexibilidade']
        if value and value not in valid_goals:
            raise serializers.ValidationError(
                f"Objetivo de fitness inválido. Os valores válidos são: {', '.join(valid_goals)}"
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user
