from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Diet, DietFeedback, MEAL_CHOICES
from .serializers import DietSerializer, DietFeedbackSerializer, DietGenerateInputSerializer, DailyDietPlanSerializer, SuggestedMealSerializer
from .filters import DietFilter
import json
from django.db.models import Sum
from django.utils import timezone
from collections import defaultdict

# IA fictícia para ajustar dieta (mantido como estava)
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
        # CORRIGIDO: Usando 'rating' em vez de 'nota' para feedback
        rating = int(request.data.get('rating', 3))
        notes = request.data.get('notes', '')
        DietFeedback.objects.create(diet=diet, user=request.user, rating=rating, feedback_text=notes)
        ajustar_dieta(diet, rating)
        serializer = DietSerializer(diet)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_diet(request):
    user = request.user
    
    serializer = DietGenerateInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    goal = serializer.validated_data.get('goal')
    calories_target = serializer.validated_data.get('calories_target')
    meals_count = serializer.validated_data.get('meals_count')
    dietary_restrictions = serializer.validated_data.get('dietary_restrictions', [])
    preferred_cuisine = serializer.validated_data.get('preferred_cuisine') # Adicionado

    generated_diets_data = []
    
    if meals_count > 0:
        calories_per_meal = calories_target / meals_count
        protein_per_meal = (calories_target * 0.3 / 4) / meals_count
        carbs_per_meal = (calories_target * 0.4 / 4) / meals_count
        fat_per_meal = (calories_target * 0.3 / 9) / meals_count
    else:
        calories_per_meal = 0
        protein_per_meal = 0
        carbs_per_meal = 0
        fat_per_meal = 0

    meal_types_available = [choice[0] for choice in MEAL_CHOICES]
    
    for i in range(meals_count):
        meal_type = meal_types_available[i % len(meal_types_available)]
        
        diet_entry = Diet.objects.create(
            user=user,
            meal=meal_type,
            calories=round(calories_per_meal),
            protein=round(protein_per_meal, 2),
            carbs=round(carbs_per_meal, 2),
            fat=round(fat_per_meal, 2),
            # date é auto_now_add=True no modelo, então não precisa ser passado aqui
        )
        # Usar SuggestedMealSerializer para formatar cada refeição individualmente
        generated_diets_data.append(SuggestedMealSerializer(diet_entry).data)

    # Criar um DailyDietPlan fictício para a resposta, já que o frontend espera isso
    # Este 'id' é apenas um placeholder para o frontend, pois não há um modelo DailyDietPlan no backend
    # Você pode usar o ID do primeiro item gerado ou um timestamp
    daily_plan_id = generated_diets_data[0]['id'] if generated_diets_data else 1 
    
    response_data = {
        "id": daily_plan_id, # ID fictício
        "user": user.id,
        "date": timezone.now().date().isoformat(), # Data atual
        "target_calories": calories_target,
        "target_protein": round(calories_target * 0.3 / 4),
        "target_carbs": round(calories_target * 0.4 / 4),
        "target_fat": round(calories_target * 0.3 / 9),
        "water_intake_ml": 2000, # Valor padrão ou calculado
        "suggested_meals": generated_diets_data,
        "macro_distribution_percentage": {
            "protein": 30, # Exemplo
            "carbs": 40, # Exemplo
            "fat": 30 # Exemplo
        },
        "rating": None, # Sem rating inicial
        "created_at": timezone.now().isoformat(),
        "updated_at": timezone.now().isoformat(),
    }

    return Response(DailyDietPlanSerializer(response_data).data, status=status.HTTP_201_CREATED)


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

    # CORRIGIDO: Usando 'rating' e 'notes' para feedback
    rating = request.data.get('rating')
    notes = request.data.get('notes', '')

    if rating is None:
        return Response({'detail': 'Nota é obrigatória.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        rating = int(rating)
    except ValueError:
        return Response({'detail': 'Nota deve ser um número inteiro.'}, status=status.HTTP_400_BAD_REQUEST)

    if rating < 1 or rating > 5:
        return Response({'detail': 'A nota deve estar entre 1 e 5.'}, status=status.HTTP_400_BAD_REQUEST)

    DietFeedback.objects.create(
        diet=diet,
        user=request.user,
        rating=rating,
        feedback_text=notes
    )
    ajustar_dieta(diet, rating)

    return Response({'detail': 'Feedback registrado com sucesso!'}, status=status.HTTP_201_CREATED)

# NOVO ENDPOINT PARA OBTER PLANOS DE DIETA DIÁRIOS AGREGADOS
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_daily_diet_plans(request):
    user = request.user
    # Busca todas as refeições do usuário
    user_diets = Diet.objects.filter(user=user).order_by('-date', 'meal')

    # Agrupa as refeições por data
    daily_plans_grouped = defaultdict(lambda: {
        'suggested_meals': [],
        'total_calories': 0,
        'total_protein': 0,
        'total_carbs': 0,
        'total_fat': 0,
        'ratings': [], # Para calcular o rating médio
        'id': None, # Usaremos o ID do primeiro Diet do dia ou um ID fictício
        'created_at': None,
        'updated_at': None,
    })

    for diet_entry in user_diets:
        date_key = diet_entry.date.isoformat()
        
        # Define o ID do plano diário como o ID do primeiro Diet do dia
        if daily_plans_grouped[date_key]['id'] is None:
            daily_plans_grouped[date_key]['id'] = diet_entry.id # Usar o ID do primeiro Diet como ID do plano
            daily_plans_grouped[date_key]['created_at'] = diet_entry.created_at.isoformat()
            daily_plans_grouped[date_key]['updated_at'] = diet_entry.updated_at.isoformat()

        daily_plans_grouped[date_key]['user'] = user.id
        daily_plans_grouped[date_key]['date'] = date_key
        daily_plans_grouped[date_key]['suggested_meals'].append(SuggestedMealSerializer(diet_entry).data)
        daily_plans_grouped[date_key]['total_calories'] += diet_entry.calories
        daily_plans_grouped[date_key]['total_protein'] += diet_entry.protein
        daily_plans_grouped[date_key]['total_carbs'] += diet_entry.carbs
        daily_plans_grouped[date_key]['total_fat'] += diet_entry.fat

        # Coleta os ratings de feedback para este Diet
        feedbacks = DietFeedback.objects.filter(diet=diet_entry)
        for feedback in feedbacks:
            daily_plans_grouped[date_key]['ratings'].append(feedback.rating)

    # Converte para a lista de DailyDietPlan formatada
    final_daily_plans = []
    for date_key, data in daily_plans_grouped.items():
        avg_rating = sum(data['ratings']) / len(data['ratings']) if data['ratings'] else None
        
        # Calculando as metas de macronutrientes de forma fictícia para o plano diário
        # Você pode ajustar esta lógica para ser mais precisa com base nos seus requisitos
        total_calories_for_macros = data['total_calories']
        target_protein = round(total_calories_for_macros * 0.3 / 4) # Ex: 30% de calorias de proteína
        target_carbs = round(total_calories_for_macros * 0.4 / 4) # Ex: 40% de calorias de carboidratos
        target_fat = round(total_calories_for_macros * 0.3 / 9) # Ex: 30% de calorias de gordura

        daily_plan_data = {
            'id': data['id'],
            'user': data['user'],
            'date': data['date'],
            'target_calories': round(data['total_calories']),
            'target_protein': target_protein,
            'target_carbs': target_carbs,
            'target_fat': target_fat,
            'water_intake_ml': 2000, # Valor padrão ou de perfil do usuário
            'suggested_meals': data['suggested_meals'],
            'macro_distribution_percentage': {
                'protein': round((data['total_protein'] * 4 / data['total_calories']) * 100) if data['total_calories'] else 0,
                'carbs': round((data['total_carbs'] * 4 / data['total_calories']) * 100) if data['total_calories'] else 0,
                'fat': round((data['total_fat'] * 9 / data['total_calories']) * 100) if data['total_calories'] else 0,
            },
            'rating': avg_rating,
            'created_at': data['created_at'],
            'updated_at': data['updated_at'],
        }
        final_daily_plans.append(DailyDietPlanSerializer(daily_plan_data).data)

    return Response(final_daily_plans, status=status.HTTP_200_OK)
