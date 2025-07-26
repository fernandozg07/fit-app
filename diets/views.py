from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Diet, DietFeedback, MEAL_CHOICES, GOAL_CHOICES # Importar GOAL_CHOICES
from .serializers import DietSerializer, DietFeedbackSerializer, DietGenerateInputSerializer, DailyDietPlanSerializer, SuggestedMealSerializer
from .filters import DietFilter
import json
from django.db.models import Sum
from django.utils import timezone
from collections import defaultdict

# IA fictícia para ajustar dieta (mantido como estava)
def ajustar_dieta(diet, rating):
    """
    Função fictícia para ajustar a dieta com base no feedback.
    Em um cenário real, você integraria sua lógica de IA aqui.
    """
    if rating >= 4:
        diet.calories += 100
    elif rating <= 2:
        diet.calories = max(1200, diet.calories - 100)
    diet.save()

class DietViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD em Dietas (refeições individuais).
    """
    queryset = Diet.objects.all()
    serializer_class = DietSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DietFilter

    def perform_create(self, serializer):
        """
        Associa o usuário autenticado à dieta ao criá-la.
        """
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
        Retorna apenas as dietas do usuário autenticado.
        """
        return Diet.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='feedback')
    def feedback(self, request, pk=None):
        """
        Endpoint para registrar feedback sobre uma dieta específica.
        """
        diet = self.get_object()
        rating = int(request.data.get('rating', 3)) # Espera 'rating' do frontend
        notes = request.data.get('notes', '')

        # Cria um registro de feedback
        DietFeedback.objects.create(diet=diet, user=request.user, rating=rating, feedback_text=notes)
        
        # Ajusta a dieta com base no feedback (lógica fictícia)
        ajustar_dieta(diet, rating)
        
        serializer = DietSerializer(diet)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_diet(request):
    """
    Gera um plano de dieta diário com base nos parâmetros fornecidos pelo usuário.
    Cria múltiplas entradas Diet no banco de dados e retorna um DailyDietPlan agregado.
    """
    user = request.user
    
    serializer = DietGenerateInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    goal = serializer.validated_data.get('goal')
    calories_target = serializer.validated_data.get('calories_target')
    meals_count = serializer.validated_data.get('meals_count')
    dietary_restrictions = serializer.validated_data.get('dietary_restrictions', [])
    preferred_cuisine = serializer.validated_data.get('preferred_cuisine')

    generated_diets_data = [] # Lista para armazenar as refeições geradas e serializadas
    
    # Calcula a distribuição de macronutrientes por refeição
    if meals_count > 0 and calories_target:
        calories_per_meal = calories_target / meals_count
        protein_per_meal = (calories_target * 0.3 / 4) / meals_count
        carbs_per_meal = (calories_target * 0.4 / 4) / meals_count
        fat_per_meal = (calories_target * 0.3 / 9) / meals_count
    else:
        calories_per_meal = 0
        protein_per_meal = 0
        carbs_per_meal = 0
        fat_per_meal = 0

    meal_types_available = [choice[0] for choice in MEAL_CHOICES] # Obtém os tipos de refeição disponíveis
    
    for i in range(meals_count):
        meal_type = meal_types_available[i % len(meal_types_available)]
        
        # Simulação de geração de detalhes da refeição pela IA
        # Em um cenário real, você integraria sua IA aqui para gerar nomes, descrições, etc.
        meal_name = f"Refeição de {meal_type.replace('_', ' ').capitalize()}"
        meal_description = f"Uma opção saudável e balanceada para o {meal_type.replace('_', ' ').lower()}, focada em seu objetivo de {goal.replace('_', ' ')}."
        meal_ingredients = [f"Ingrediente A {i+1}", f"Ingrediente B {i+1}", f"Ingrediente C {i+1}"]
        meal_preparation_time = 20 + (i * 5) # Exemplo de tempo de preparo variável

        # Cria uma entrada Diet para cada refeição gerada
        diet_entry = Diet.objects.create(
            user=user,
            meal=meal_type,
            calories=round(calories_per_meal),
            protein=round(protein_per_meal, 2),
            carbs=round(carbs_per_meal, 2),
            fat=round(fat_per_meal, 2),
            
            # Salvando os detalhes adicionais da refeição
            name=meal_name,
            description=meal_description,
            ingredients=meal_ingredients,
            preparation_time_minutes=meal_preparation_time,
            
            # Salvando os parâmetros da solicitação de geração no modelo Diet
            goal=goal,
            dietary_restrictions=dietary_restrictions,
            preferred_cuisine=preferred_cuisine,
            target_calories=calories_target,
            target_protein=round(calories_target * 0.3 / 4) if calories_target else None,
            target_carbs=round(calories_target * 0.4 / 4) if calories_target else None,
            target_fat=round(calories_target * 0.3 / 9) if calories_target else None,
            water_intake_ml=2000, # Valor padrão, pode ser gerado pela IA ou do perfil do usuário
            rating=None, # Sem rating inicial para a refeição
        )
        # Serializa a refeição gerada usando SuggestedMealSerializer
        generated_diets_data.append(SuggestedMealSerializer(diet_entry).data)

    # Agrega os dados para formar a resposta DailyDietPlan
    daily_plan_id = generated_diets_data[0]['id'] if generated_diets_data else 1 # ID fictício
    
    response_data = {
        "id": daily_plan_id,
        "user": user.id,
        "date": timezone.now().date().isoformat(),
        "target_calories": calories_target,
        "target_protein": round(calories_target * 0.3 / 4) if calories_target else 0,
        "target_carbs": round(calories_target * 0.4 / 4) if calories_target else 0,
        "target_fat": round(calories_target * 0.3 / 9) if calories_target else 0,
        "water_intake_ml": 2000,
        "suggested_meals": generated_diets_data,
        "macro_distribution_percentage": {
            "protein": round((sum(d['protein'] for d in generated_diets_data) * 4 / sum(d['calories'] for d in generated_diets_data)) * 100) if sum(d['calories'] for d in generated_diets_data) else 0,
            "carbs": round((sum(d['carbs'] for d in generated_diets_data) * 4 / sum(d['calories'] for d in generated_diets_data)) * 100) if sum(d['calories'] for d in generated_diets_data) else 0,
            "fat": round((sum(d['fat'] for d in generated_diets_data) * 9 / sum(d['calories'] for d in generated_diets_data)) * 100) if sum(d['calories'] for d in generated_diets_data) else 0,
        },
        "rating": None, # Sem rating inicial para o plano diário
        "created_at": timezone.now().isoformat(),
        "updated_at": timezone.now().isoformat(),
    }

    return Response(DailyDietPlanSerializer(response_data).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_diet(request):
    """
    Registra uma dieta (refeição individual) no banco de dados.
    """
    serializer = DietSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({'detail': 'Dieta registrada com sucesso!', 'diet': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_diet_feedback(request, diet_id):
    """
    Envia feedback para uma refeição de dieta específica.
    """
    try:
        diet = Diet.objects.get(id=diet_id, user=request.user)
    except Diet.DoesNotExist:
        return Response({'detail': 'Dieta não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    rating = request.data.get('rating')
    notes = request.data.get('notes', '')

    if rating is None:
        return Response({'detail': 'Avaliação (rating) é obrigatória.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        rating = int(rating)
    except ValueError:
        return Response({'detail': 'Avaliação (rating) deve ser um número inteiro.'}, status=status.HTTP_400_BAD_REQUEST)

    if rating < 1 or rating > 5:
        return Response({'detail': 'A avaliação (rating) deve estar entre 1 e 5.'}, status=status.HTTP_400_BAD_REQUEST)

    DietFeedback.objects.create(
        diet=diet,
        user=request.user,
        rating=rating,
        feedback_text=notes
    )
    ajustar_dieta(diet, rating)

    return Response({'detail': 'Feedback registrado com sucesso!'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_daily_diet_plans(request):
    """
    Retorna planos de dieta diários agregados para o usuário autenticado.
    Agrupa as refeições por data e calcula totais e médias diárias.
    """
    user = request.user
    # Busca todas as refeições do usuário, ordenadas por data e depois por tipo de refeição
    user_diets = Diet.objects.filter(user=user).order_by('-date', 'meal')

    # Usa defaultdict para agrupar refeições por data
    daily_plans_grouped = defaultdict(lambda: {
        'suggested_meals': [],
        'total_calories': 0,
        'total_protein': 0,
        'total_carbs': 0,
        'total_fat': 0,
        'ratings': [], # Para coletar todos os ratings de feedback para o dia
        'id': None, # Será o ID do primeiro Diet do dia ou um ID fictício
        'created_at': None,
        'updated_at': None,
        # Campos de meta do plano diário, puxados do primeiro Diet do dia
        'target_calories': None,
        'target_protein': None,
        'target_carbs': None,
        'target_fat': None,
        'water_intake_ml': None,
    })

    for diet_entry in user_diets:
        date_key = diet_entry.date.isoformat()
        
        # Define o ID do plano diário como o ID do primeiro Diet do dia
        # E puxa os campos de meta do plano diário do primeiro Diet para o dia
        if daily_plans_grouped[date_key]['id'] is None:
            daily_plans_grouped[date_key]['id'] = diet_entry.id
            daily_plans_grouped[date_key]['created_at'] = diet_entry.created_at.isoformat()
            daily_plans_grouped[date_key]['updated_at'] = diet_entry.updated_at.isoformat()
            daily_plans_grouped[date_key]['target_calories'] = diet_entry.target_calories
            daily_plans_grouped[date_key]['target_protein'] = diet_entry.target_protein
            daily_plans_grouped[date_key]['target_carbs'] = diet_entry.target_carbs
            daily_plans_grouped[date_key]['target_fat'] = diet_entry.target_fat
            daily_plans_grouped[date_key]['water_intake_ml'] = diet_entry.water_intake_ml

        # Adiciona os detalhes da refeição e acumula os totais de macronutrientes
        daily_plans_grouped[date_key]['user'] = user.id
        daily_plans_grouped[date_key]['date'] = date_key
        daily_plans_grouped[date_key]['suggested_meals'].append(SuggestedMealSerializer(diet_entry).data)
        daily_plans_grouped[date_key]['total_calories'] += diet_entry.calories
        daily_plans_grouped[date_key]['total_protein'] += diet_entry.protein
        daily_plans_grouped[date_key]['total_carbs'] += diet_entry.carbs
        daily_plans_grouped[date_key]['total_fat'] += diet_entry.fat

        # Coleta os ratings de feedback para esta refeição específica
        feedbacks = DietFeedback.objects.filter(diet=diet_entry)
        for feedback in feedbacks:
            daily_plans_grouped[date_key]['ratings'].append(feedback.rating)

    # Converte o defaultdict para a lista final de DailyDietPlan formatada
    final_daily_plans = []
    for date_key, data in daily_plans_grouped.items():
        # Calcula o rating médio do plano diário
        avg_rating = sum(data['ratings']) / len(data['ratings']) if data['ratings'] else None
        
        # Usa os valores de target salvos no primeiro Diet do dia
        target_calories = data['target_calories']
        target_protein = data['target_protein']
        target_carbs = data['target_carbs']
        target_fat = data['target_fat']
        water_intake_ml = data['water_intake_ml']

        daily_plan_data = {
            'id': data['id'],
            'user': data['user'],
            'date': data['date'],
            'target_calories': target_calories,
            'target_protein': target_protein,
            'target_carbs': target_carbs,
            'target_fat': target_fat,
            'water_intake_ml': water_intake_ml,
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
