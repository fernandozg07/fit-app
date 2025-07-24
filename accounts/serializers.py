from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(write_only=True, min_length=6, required=False) # password não é obrigatório para UPDATE

    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'first_name', 'last_name',
            'age', 'birth_date', 'weight', 'height',
            'fitness_goal', 'dietary_restrictions', 'activity_level' # <--- ADICIONADO activity_level
        ]
        read_only_fields = ['id', 'age', 'email'] # email também deve ser read_only para PATCH
                                                    # birth_date pode ser editável ou read_only dependendo da sua escolha
        extra_kwargs = {
            'birth_date': {'required': False, 'allow_null': True},
            'weight': {'required': False, 'allow_null': True},
            'height': {'required': False, 'allow_null': True},
            'fitness_goal': {'required': False, 'allow_null': True},
            'dietary_restrictions': {'required': False, 'allow_blank': True, 'allow_null': True},
            'activity_level': {'required': False, 'allow_null': True}, # <--- ADICIONADO activity_level
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
        valid_goals = [choice[0] for choice in User.FITNESS_GOALS] # Pega as escolhas do modelo
        if value and value not in valid_goals:
            raise serializers.ValidationError(
                f"Objetivo de fitness inválido. Valores válidos: {', '.join(valid_goals)}."
            )
        return value
    
    # <--- ADICIONAR ESTA VALIDAÇÃO PARA activity_level
    def validate_activity_level(self, value):
        valid_levels = [choice[0] for choice in User.ACTIVITY_LEVELS]
        if value and value not in valid_levels:
            raise serializers.ValidationError(
                f"Nível de atividade inválido. Valores válidos: {', '.join(valid_levels)}."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({"password": "Senha obrigatória para cadastro."})
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            if attr == 'email': # Não permite alterar o email via PATCH simples aqui
                continue 
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
