from rest_framework import serializers
from .models import ProgressEntry

class ProgressEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressEntry
        # Inclui todos os campos do modelo para serialização/desserialização
        fields = '__all__' 
        # 'user' é definido automaticamente na view, então é read-only para o cliente
        read_only_fields = ['user', 'created_at', 'updated_at'] 

    def validate_weight(self, value):
        if value is None or value <= 0: # Adicionado verificação para None
            raise serializers.ValidationError("O peso deve ser um número positivo maior que zero.")
        return value

    def validate_body_fat(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("A gordura corporal não pode ser negativa.")
        return value

    def validate_muscle_mass(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("A massa muscular não pode ser negativa.")
        return value

    # Adicionadas validações para os novos campos de circunferência e água, se existirem
    def validate_arm_circumference(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("A circunferência do braço não pode ser negativa.")
        return value

    def validate_chest_circumference(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("A circunferência do peito não pode ser negativa.")
        return value
    
    def validate_waist_circumference(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("A circunferência da cintura não pode ser negativa.")
        return value

    def validate_hip_circumference(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("A circunferência do quadril não pode ser negativa.")
        return value

    def validate_thigh_circumference(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("A circunferência da coxa não pode ser negativa.")
        return value

    def validate_calf_circumference(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("A circunferência da panturrilha não pode ser negativa.")
        return value

    def create(self, validated_data):
        # O usuário é automaticamente associado pelo perform_create no ViewSet,
        # então não é estritamente necessário definir aqui, mas não causa problema.
        # validated_data['user'] = self.context['request'].user 
        return super().create(validated_data)

