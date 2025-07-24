from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Diet, DietFeedback, MEAL_CHOICES # Importe MEAL_CHOICES
from .serializers import DietSerializer, DietFeedbackSerializer, DietGenerateInputSerializer # Importe o novo serializer
from .filters import DietFilter 

# IA fictícia para ajustar dieta
def ajustar_dieta(diet, rating):
    if rating >= 4:
        diet.calories += 100
    elif rating <= 2:
        diet.calories = max(1200, diet.calories - 100)
    diet.save()
    

class DietViewSet(viewsets.ModelViewSet):
    queryset = Diet.objects.all()
    serializer_class = DietSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DietFilter

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Diet.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='feedback')
    def feedback(self, request, pk=None):
        diet = self.get_object()
        nota = int(request.data.get('nota', 3))
        texto = request.data.get('texto', '')
        DietFeedback.objects.create(diet=diet, user=request.user, rating=nota, feedback_text=texto)
        ajustar_dieta(diet, nota) 
        serializer = DietSerializer(diet) 
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_diet(request):
    user = request.user
    
    # Valida os dados de entrada usando o novo serializer
    serializer = DietGenerateInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Extrai os dados validados
    goal = serializer.validated_data.get('goal')
    calories_target = serializer.has_key('calories_target')
    meals_count = serializer.validated_data.get('meals_count')
    dietary_restrictions = serializer.validated_data.get('dietary_restrictions', [])

    # Lógica simplificada para gerar refeições com base nos dados de entrada
    # Esta é uma adaptação para o modelo Diet atual (que registra refeições individuais).
    # Se você precisar de um "plano de dieta" mais complexo, o modelo Diet precisará ser expandido.
    generated_diets_data = []
    
    # Distribui as calorias e macros de forma simplificada entre as refeições
    # Esta é uma lógica de exemplo e pode ser muito mais sofisticada com IA real.
    calories_per_meal = calories_target / meals_count
    protein_per_meal = (calories_target * 0.3 / 4) / meals_count # Ex: 30% de calorias de proteína
    carbs_per_meal = (calories_target * 0.4 / 4) / meals_count # Ex: 40% de calorias de carboidratos
    fat_per_meal = (calories_target * 0.3 / 9) / meals_count # Ex: 30% de calorias de gordura

    # Mapeia as escolhas de refeição do modelo para uma lista de strings
    meal_types_available = [choice[0] for choice in MEAL_CHOICES]
    
    for i in range(meals_count):
        # Atribui um tipo de refeição de forma cíclica ou baseada em lógica mais complexa
        meal_type = meal_types_available[i % len(meal_types_available)] 
        
        diet_entry = Diet.objects.create(
            user=user,
            meal=meal_type,
            calories=round(calories_per_meal),
            protein=round(protein_per_meal, 2),
            carbs=round(carbs_per_meal, 2),
            fat=round(fat_per_meal, 2)
        )
        generated_diets_data.append(DietSerializer(diet_entry).data)

    return Response({
        'detail': f'Dieta com {meals_count} refeições gerada com sucesso!',
        'diets': generated_diets_data # Retorna uma lista de dietas (refeições)
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_diet(request):
    serializer = DietSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({'detail': 'Dieta registrada com sucesso!', 'diet': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_diet_feedback(request, diet_id):
    try:
        diet = Diet.objects.get(id=diet_id, user=request.user)
    except Diet.DoesNotExist:
        return Response({'detail': 'Dieta não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    nota = request.data.get('nota')
    texto = request.data.get('texto', '')

    if nota is None:
        return Response({'detail': 'Nota é obrigatória.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        nota = int(nota)
    except ValueError:
        return Response({'detail': 'Nota deve ser um número inteiro.'}, status=status.HTTP_400_BAD_REQUEST)

    if nota < 1 or nota > 5:
        return Response({'detail': 'A nota deve estar entre 1 e 5.'}, status=status.HTTP_400_BAD_REQUEST)

    DietFeedback.objects.create(
        diet=diet,
        user=request.user,
        rating=nota,
        feedback_text=texto
    )
    ajustar_dieta(diet, nota)

    return Response({'detail': 'Feedback registrado com sucesso!'}, status=status.HTTP_201_CREATED)
