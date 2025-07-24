from rest_framework import serializers
from .models import ProgressEntry

class ProgressEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressEntry
        fields = '__all__'
        read_only_fields = ['user']

    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError("O peso deve ser maior que zero.")
        return value

    def validate_body_fat(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("A gordura corporal não pode ser negativa.")
        return value

    def validate_muscle_mass(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("A massa muscular não pode ser negativa.")
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

