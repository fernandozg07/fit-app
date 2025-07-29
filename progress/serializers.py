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
        if value is None or value <= 0:
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
        return super().create(validated_data)

class ProgressStatsSerializer(serializers.Serializer):
    """
    Serializa os dados retornados pela ProgressStatsView.
    """
    total_entries = serializers.IntegerField(help_text="Número total de registros de progresso.")
    avg_weight = serializers.FloatField(help_text="Peso médio registrado.")
    max_weight = serializers.FloatField(allow_null=True, help_text="Peso máximo registrado.")
    min_weight = serializers.FloatField(allow_null=True, help_text="Peso mínimo registrado.")
    avg_body_fat = serializers.FloatField(help_text="Percentual médio de gordura corporal.")
    avg_muscle_mass = serializers.FloatField(help_text="Massa muscular média.")
    current_weight = serializers.FloatField(allow_null=True, help_text="Peso atual (último registro).")
    initial_weight = serializers.FloatField(allow_null=True, help_text="Peso inicial (primeiro registro).")
    weight_change = serializers.FloatField(allow_null=True, help_text="Mudança total de peso desde o primeiro registro.")
    bmi = serializers.FloatField(allow_null=True, help_text="Índice de Massa Corporal (IMC) com base no peso atual e altura do usuário.")
    total_workouts = serializers.IntegerField(help_text="Número total de treinos registrados.")
    active_days = serializers.IntegerField(help_text="Número de dias com treinos registrados.")
    average_workout_duration = serializers.FloatField(help_text="Duração média dos treinos em minutos.")
    calories_burned_total = serializers.IntegerField(help_text="Total de calorias queimadas (se disponível nos logs de treino).")
    calories_consumed_total = serializers.IntegerField(help_text="Total de calorias consumidas.")