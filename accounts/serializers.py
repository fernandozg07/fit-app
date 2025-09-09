from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField(read_only=True)
    # Senha é write-only (não é retornada na resposta) e não é obrigatória para atualizações
    password = serializers.CharField(write_only=True, min_length=6, required=False) 

    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'first_name', 'last_name',
            'age', 'birth_date', 'weight', 'height',
            'fitness_goal', 'dietary_restrictions', 'activity_level', 'gender' # Adicionado 'gender'
        ]
        # Campos que só podem ser lidos (não podem ser alterados via serializer)
        read_only_fields = ['id', 'age', 'email'] 
        
        # Configurações adicionais para campos específicos
        extra_kwargs = {
            'birth_date': {'required': False, 'allow_null': True},
            'weight': {'required': False, 'allow_null': True},
            'height': {'required': False, 'allow_null': True},
            'fitness_goal': {'required': False, 'allow_null': True},
            'dietary_restrictions': {'required': False, 'allow_blank': True, 'allow_null': True},
            'activity_level': {'required': False, 'allow_null': True},
            'gender': {'required': False, 'allow_null': True}, # Adicionado 'gender'
        }

    def get_age(self, obj):
        """
        Calcula a idade do usuário com base na data de nascimento.
        """
        if obj.birth_date:
            today = date.today()
            return today.year - obj.birth_date.year - (
                (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day)
            )
        return None

    def validate_weight(self, value):
        """
        Valida que o peso seja um valor positivo.
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError("O peso deve ser um valor positivo.")
        return value

    def validate_height(self, value):
        """
        Valida que a altura seja um valor positivo.
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError("A altura deve ser um valor positivo.")
        return value

    def validate_fitness_goal(self, value):
        """
        Valida que o objetivo de fitness seja uma das opções válidas do modelo User.
        """
        valid_goals = [choice[0] for choice in User.FITNESS_GOALS] 
        if value and value not in valid_goals:
            raise serializers.ValidationError(
                f"Objetivo de fitness inválido. Valores válidos: {', '.join(valid_goals)}."
            )
        return value
    
    def validate_activity_level(self, value):
        """
        Valida que o nível de atividade seja uma das opções válidas do modelo User.
        """
        valid_levels = [choice[0] for choice in User.ACTIVITY_LEVELS]
        if value and value not in valid_levels:
            raise serializers.ValidationError(
                f"Nível de atividade inválido. Valores válidos: {', '.join(valid_levels)}."
            )
        return value

    def validate_gender(self, value):
        """
        Valida que o gênero seja uma das opções válidas do modelo User.
        """
        valid_genders = [choice[0] for choice in User.GENDER_CHOICES]
        if value and value not in valid_genders:
            raise serializers.ValidationError(
                f"Gênero inválido. Valores válidos: {', '.join(valid_genders)}."
            )
        return value

    def create(self, validated_data):
        """
        Cria um novo usuário, tratando a senha separadamente para hash.
        """
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({"password": "Senha obrigatória para cadastro."})
        user = User(**validated_data)
        user.set_password(password) # Hash da senha
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Atualiza um usuário existente, tratando a senha separadamente.
        Não permite a alteração do email.
        """
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            if attr == 'email': # Impede a alteração do email via update
                continue 
            setattr(instance, attr, value)
        if password:
            instance.set_password(password) # Hash da nova senha
        instance.save()
        return instance
