import datetime
import random # Importar para usar random.choice ou random.shuffle
from types import SimpleNamespace
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Diet, DietFeedback, MEAL_CHOICES, GOAL_CHOICES
from .serializers import DietSerializer, DietFeedbackSerializer, DietGenerateInputSerializer, DailyDietPlanSerializer, SuggestedMealSerializer
from .filters import DietFilter
from django.utils import timezone
from collections import defaultdict

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
        if self.request.user.is_authenticated:
            # Ordenar por data decrescente para planos diários mais recentes primeiro
            # e por 'meal' para ter uma ordem consistente das refeições dentro do dia.
            return Diet.objects.filter(user=self.request.user).order_by('-date', 'meal')
        return Diet.objects.none()

    def list(self, request, *args, **kwargs):
        user = request.user
        user_diets = self.get_queryset()

        daily_plans_grouped = defaultdict(lambda: {
            'suggested_meals': [],
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fat': 0,
            'ratings': [],
            'id': None,
            'created_at': None,
            'updated_at': None,
            'target_calories': None,
            'target_protein': None,
            'target_carbs': None,
            'target_fat': None,
            'water_intake_ml': None,
            'actual_date_obj': None,
            'user': user.id,
        })

        for diet_entry in user_diets:
            date_key = diet_entry.date.isoformat()

            # Se for a primeira entrada para esta data, inicialize os metadados do plano diário
            if daily_plans_grouped[date_key]['id'] is None:
                daily_plans_grouped[date_key]['id'] = diet_entry.id # Usar o ID da primeira refeição como ID do plano (pode ser melhorado para um ID de plano diário real se existir)
                daily_plans_grouped[date_key]['created_at'] = diet_entry.created_at
                daily_plans_grouped[date_key]['updated_at'] = diet_entry.updated_at
                daily_plans_grouped[date_key]['target_calories'] = diet_entry.target_calories
                daily_plans_grouped[date_key]['target_protein'] = diet_entry.target_protein
                daily_plans_grouped[date_key]['target_carbs'] = diet_entry.target_carbs
                daily_plans_grouped[date_key]['target_fat'] = diet_entry.target_fat
                daily_plans_grouped[date_key]['water_intake_ml'] = diet_entry.water_intake_ml
                daily_plans_grouped[date_key]['actual_date_obj'] = diet_entry.date

            daily_plans_grouped[date_key]['suggested_meals'].append(diet_entry)
            daily_plans_grouped[date_key]['total_calories'] += diet_entry.calories
            daily_plans_grouped[date_key]['total_protein'] += diet_entry.protein
            daily_plans_grouped[date_key]['total_carbs'] += diet_entry.carbs
            daily_plans_grouped[date_key]['total_fat'] += diet_entry.fat

            feedbacks = DietFeedback.objects.filter(diet=diet_entry)
            for feedback in feedbacks:
                daily_plans_grouped[date_key]['ratings'].append(feedback.rating)

        final_daily_plans = []
        # Sort by date in descending order before sending
        sorted_dates = sorted(daily_plans_grouped.keys(), reverse=True)
        
        for date_key in sorted_dates:
            data = daily_plans_grouped[date_key]
            avg_rating = sum(data['ratings']) / len(data['ratings']) if data['ratings'] else None
            plan_date = data['actual_date_obj'] or timezone.now().date()
            total_calories_for_macros = data['total_calories'] if data['total_calories'] > 0 else 1

            daily_plan_data = {
                'id': data['id'],
                'user': data['user'],
                'date': plan_date,
                'target_calories': data['target_calories'],
                'target_protein': data['target_protein'],
                'target_carbs': data['target_carbs'],
                'target_fat': data['target_fat'],
                'water_intake_ml': data['water_intake_ml'],
                'suggested_meals': data['suggested_meals'],  # lista de instâncias Diet
                'macro_distribution_percentage': {
                    'protein': round((data['total_protein'] * 4 / total_calories_for_macros) * 100),
                    'carbs': round((data['total_carbs'] * 4 / total_calories_for_macros) * 100),
                    'fat': round((data['total_fat'] * 9 / total_calories_for_macros) * 100),
                },
                'rating': avg_rating,
                'created_at': data['created_at'],
                'updated_at': data['updated_at'],
            }
            obj = SimpleNamespace(**daily_plan_data)
            final_daily_plans.append(DailyDietPlanSerializer(obj).data)

        return Response(final_daily_plans, status=status.HTTP_200_OK)


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
    preferred_cuisine = serializer.validated_data.get('preferred_cuisine')

    generated_diets = []

    # Definição de proporções de calorias e macros por tipo de refeição
    # Estas proporções são exemplos e podem ser ajustadas. A soma das 'calories_pct' deve ser ~1.0
    # para a distribuição ideal do total de calorias alvo.
    # Exemplo para 3 refeições: café (0.25), almoço (0.40), jantar (0.35)
    # Exemplo para 6 refeições: café (0.20), lanche_manhã (0.10), almoço (0.25), lanche_tarde (0.10), jantar (0.25), lanche_noite (0.10)
    
    # Mapeamento de proporções (calorias, proteína, carboidratos, gordura)
    # Valores percentuais do total de calorias/macros da refeição, não do total diário.
    # O cálculo aqui é do PERCENTUAL DA CALORIA TOTAL DIÁRIA para aquela refeição.
    meal_distribution_pct = {
        'breakfast':     {'calories_pct': 0.20, 'protein_ratio': 0.25, 'carbs_ratio': 0.50, 'fat_ratio': 0.25}, # Ex: 25% Proteína, 50% Carbs, 25% Gordura da caloria do café
        'lunch':         {'calories_pct': 0.35, 'protein_ratio': 0.35, 'carbs_ratio': 0.40, 'fat_ratio': 0.25},
        'dinner':        {'calories_pct': 0.30, 'protein_ratio': 0.40, 'carbs_ratio': 0.30, 'fat_ratio': 0.30},
        'snack':         {'calories_pct': 0.08, 'protein_ratio': 0.30, 'carbs_ratio': 0.40, 'fat_ratio': 0.30},
        'afternoon_snack': {'calories_pct': 0.07, 'protein_ratio': 0.30, 'carbs_ratio': 0.40, 'fat_ratio': 0.30},
        'pre_workout':   {'calories_pct': 0.05, 'protein_ratio': 0.20, 'carbs_ratio': 0.60, 'fat_ratio': 0.20},
        'post_workout':  {'calories_pct': 0.05, 'protein_ratio': 0.40, 'carbs_ratio': 0.40, 'fat_ratio': 0.20},
    }
    
    # Mapeamento de conteúdo de refeições (ingredientes e descrições)
    meal_content_suggestions = {
        'breakfast': {
            'names': ["Omelete com Espinafre e Torrada Integral", "Mingau de Aveia com Frutas e Sementes", "Panquecas de Banana com Whey Protein"],
            'descriptions': [
                "Um café da manhã nutritivo e rico em proteínas para começar o dia com energia.",
                "Uma opção reconfortante e rica em fibras, ideal para saciedade e digestão.",
                "Deliciosas panquecas para um café da manhã doce e proteico."
            ],
            'ingredients': [
                ["Ovos", "Espinafre", "Pão integral", "Azeite"],
                ["Aveia", "Leite desnatado/vegetal", "Banana", "Chia", "Mel"],
                ["Banana", "Ovo", "Whey Protein", "Farinha de aveia", "Canela"]
            ]
        },
        'lunch': {
            'names': ["Frango Grelhado com Arroz Integral e Vegetais Assados", "Salmão Assado com Batata Doce e Brócolis", "Salada Completa de Grão de Bico e Quinoa"],
            'descriptions': [
                "Refeição equilibrada, com boa fonte de proteína magra e carboidratos complexos.",
                "Rica em ômega-3 e carboidratos de baixo índice glicêmico para energia duradoura.",
                "Uma opção vegetariana saborosa e cheia de fibras e proteínas."
            ],
            'ingredients': [
                ["Peito de frango", "Arroz integral", "Brócolis", "Cenoura", "Azeite"],
                ["Salmão", "Batata doce", "Brócolis", "Limão", "Azeite"],
                ["Grão de bico", "Quinoa", "Tomate cereja", "Pepino", "Folhas verdes", "Molho de limão"]
            ]
        },
        'dinner': {
            'names': ["Sopa de Legumes com Proteína Magra", "Filé de Peixe com Purê de Couve-Flor", "Omelete de Legumes com Salada Verde"],
            'descriptions': [
                "Leve e nutritiva, ideal para a noite, com baixo teor de carboidratos.",
                "Alternativa ao purê tradicional, rica em vitaminas e minerais.",
                "Jantar rápido e versátil, fácil de adaptar com os legumes de sua preferência."
            ],
            'ingredients': [
                ["Abobrinha", "Cenoura", "Frango desfiado/Lentilha", "Caldo de legumes", "Temperos"],
                ["Tilápia/Bacalhau", "Couve-flor", "Leite desnatado", "Noz-moscada"],
                ["Ovos", "Pimentão", "Cebola", "Tomate", "Alface", "Rúcula"]
            ]
        },
        'snack': {
            'names': ["Iogurte Grego com Frutas Vermelhas e Granola", "Mix de Castanhas e Frutas Secas", "Shake de Proteína com Leite Vegetal"],
            'descriptions': [
                "Um lanche rico em proteínas e antioxidantes.",
                "Fonte de gorduras saudáveis e energia rápida.",
                "Prático e eficaz para complementar a ingestão proteica."
            ],
            'ingredients': [
                ["Iogurte grego", "Morango", "Mirtilo", "Granola sem açúcar"],
                ["Amêndoas", "Nozes", "Castanha-do-pará", "Uvas passas"],
                ["Whey Protein", "Leite de amêndoas", "Gelo"]
            ]
        },
        'afternoon_snack': { # Pode ser similar ao 'snack' ou ter variações
            'names': ["Smoothie Verde Detox", "Queijo Cottage com Tomate Cereja", "Torrada de Arroz com Pasta de Amendoim"],
            'descriptions': [
                "Refrescante e cheio de nutrientes, ideal para energizar a tarde.",
                "Lanche salgado e proteico, perfeito para matar a fome.",
                "Fonte de energia e gorduras boas para o meio da tarde."
            ],
            'ingredients': [
                ["Espinafre", "Maçã verde", "Pepino", "Gengibre", "Água de coco"],
                ["Queijo cottage", "Tomate cereja", "Orégano"],
                ["Torrada de arroz", "Pasta de amendoim integral", "Canela"]
            ]
        },
        'pre_workout': {
            'names': ["Banana com Pasta de Amendoim", "Batata Doce com Frango Desfiado", "Pão Integral com Geleia"],
            'descriptions': [
                "Energia rápida e sustentada para o treino.",
                "Carboidratos complexos e proteína para evitar o catabolismo.",
                "Combinação simples de carboidratos para impulsionar o desempenho."
            ],
            'ingredients': [
                ["Banana", "Pasta de amendoim integral"],
                ["Batata doce cozida", "Frango desfiado"],
                ["Pão integral", "Geleia de frutas sem açúcar"]
            ]
        },
        'post_workout': {
            'names': ["Whey Protein com Água e Fruta", "Ovos Mexidos com Tapioca", "Atum com Arroz Branco"],
            'descriptions': [
                "Recuperação muscular rápida e reposição de glicogênio.",
                "Proteína de alto valor biológico e carboidratos de rápida absorção.",
                "Opção clássica para recuperação, combinando proteína e carboidrato."
            ],
            'ingredients': [
                ["Whey Protein", "Água", "Maçã/Banana"],
                ["Ovos", "Tapioca", "Queijo branco"],
                ["Atum em água", "Arroz branco"]
            ]
        }
    }

    # Assegurar que as proporções somem 1.0 para as refeições que serão de fato geradas
    # Isso requer uma lógica mais complexa se você quiser escolher os tipos de refeição dinamicamente.
    # Por agora, vamos usar um conjunto fixo de tipos para as `meals_count` e normalizar as proporções.

    # Seleciona os tipos de refeição a serem gerados, garantindo que não se repitam imediatamente
    # e que cubram os principais.
    selected_meal_types = []
    # Cria uma cópia da lista de escolhas para poder manipulá-la
    available_choices = list(MEAL_CHOICES) 
    
    # Priorizar refeições principais: café, almoço, jantar
    priority_meals = ['breakfast', 'lunch', 'dinner']
    random.shuffle(priority_meals) # Embaralha para que não seja sempre na mesma ordem

    for meal_type_code, _ in available_choices:
        if meal_type_code in priority_meals:
            selected_meal_types.append(meal_type_code)
            priority_meals.remove(meal_type_code) # Remove da lista de prioridade

        if len(selected_meal_types) == meals_count:
            break
    
    # Se ainda precisar de mais refeições, adicione aleatoriamente do restante
    remaining_meals = [choice[0] for choice in available_choices if choice[0] not in selected_meal_types]
    random.shuffle(remaining_meals)

    while len(selected_meal_types) < meals_count and remaining_meals:
        selected_meal_types.append(remaining_meals.pop(0)) # Adiciona da lista restante

    # Se ainda não atingiu meals_count (ex: meals_count > len(MEAL_CHOICES)), repete
    while len(selected_meal_types) < meals_count:
        selected_meal_types.append(random.choice([choice[0] for choice in MEAL_CHOICES]))


    # Calcula a soma total das proporções para as refeições selecionadas
    # Isso é crucial para normalizar e distribuir as calorias e macros totais.
    total_proportion_sum = sum(meal_distribution_pct[mt]['calories_pct'] for mt in selected_meal_types if mt in meal_distribution_pct)
    
    if total_proportion_sum == 0 and meals_count > 0: # Evita divisão por zero se nenhuma proporção for definida
        # Fallback: se não houver proporções, distribua igualmente
        calories_per_meal_base = calories_target / meals_count
        protein_per_meal_base = (calories_target * 0.3 / 4) / meals_count
        carbs_per_meal_base = (calories_target * 0.4 / 4) / meals_count
        fat_per_meal_base = (calories_target * 0.3 / 9) / meals_count
    else:
        calories_per_meal_base = 0 # Usado para calcular a parcela de cada refeição
        protein_per_meal_base = 0
        carbs_per_meal_base = 0
        fat_per_meal_base = 0

    total_target_protein = round(calories_target * 0.3 / 4) if calories_target else 0
    total_target_carbs = round(calories_target * 0.4 / 4) if calories_target else 0
    total_target_fat = round(calories_target * 0.3 / 9) if calories_target else 0


    for meal_type in selected_meal_types:
        # Pega as proporções específicas para este tipo de refeição
        proportions = meal_distribution_pct.get(meal_type, {
            'calories_pct': 1.0 / meals_count, # Fallback para distribuição igual
            'protein_ratio': 0.30, 
            'carbs_ratio': 0.40, 
            'fat_ratio': 0.30
        })

        # Calcula as calorias para esta refeição com base na proporção do total diário
        # Normaliza pela soma total das proporções selecionadas para garantir que o total seja respeitado
        if total_proportion_sum > 0:
            meal_calories = (calories_target * proportions['calories_pct']) / total_proportion_sum * meals_count 
            # O fator `* meals_count` é para compensar a divisão original da proporção, para que a soma final seja `calories_target`
            # Esta linha pode ser ajustada. Se meal_distribution_pct['calories_pct'] já representa a proporção da refeição em relação ao total diário,
            # então `meal_calories = calories_target * proportions['calories_pct']` é suficiente, contanto que as `calories_pct` somem 1.0 para as refeições escolhidas.
            # A forma mais simples de fazer isso é calcular `calories_per_meal` para cada um baseado na % que aquela refeição representa do dia.
        else:
            meal_calories = calories_per_meal_base # Fallback: distribuição igual

        # Calcula as macros para esta refeição com base nas calorias da refeição
        meal_protein = (meal_calories * proportions['protein_ratio']) / 4
        meal_carbs = (meal_calories * proportions['carbs_ratio']) / 4
        meal_fat = (meal_calories * proportions['fat_ratio']) / 9

        # Pega conteúdo descritivo da refeição
        content = meal_content_suggestions.get(meal_type, {
            'names': [f"Refeição {meal_type.replace('_', ' ').capitalize()}"],
            'descriptions': [f"Uma refeição de {round(meal_calories, 2)} kcal para {meal_type.replace('_', ' ').lower()}."],
            'ingredients': [["Ingredientes genéricos para", meal_type]]
        })

        meal_name = random.choice(content['names'])
        meal_description = random.choice(content['descriptions'])
        meal_ingredients = random.choice(content['ingredients'])
        
        # Gera um tempo de preparo aleatório mais realista
        meal_preparation_time = random.randint(15, 60) 

        diet_entry = Diet.objects.create(
            user=user,
            meal=meal_type,
            calories=round(meal_calories, 2),
            protein=round(meal_protein, 2),
            carbs=round(meal_carbs, 2),
            fat=round(meal_fat, 2),
            name=meal_name,
            description=meal_description,
            ingredients=meal_ingredients,
            preparation_time_minutes=meal_preparation_time,
            goal=goal,
            dietary_restrictions=dietary_restrictions,
            preferred_cuisine=preferred_cuisine,
            target_calories=calories_target, # Estes são os alvos diários
            target_protein=total_target_protein,
            target_carbs=total_target_carbs,
            target_fat=total_target_fat,
            water_intake_ml=2000, # Pode ser dinâmico no futuro
            rating=None,
        )
        generated_diets.append(diet_entry)

    total_generated_calories = sum(d.calories for d in generated_diets)
    total_generated_protein = sum(d.protein for d in generated_diets)
    total_generated_carbs = sum(d.carbs for d in generated_diets)
    total_generated_fat = sum(d.fat for d in generated_diets)

    # Verifica se há dietas geradas para evitar erro de índice
    first_diet_id = generated_diets[0].id if generated_diets else None
    
    response_data = {
        "id": first_diet_id, # Usar o ID da primeira refeição como ID do "plano" é um workaround.
                             # Idealmente, você teria um modelo `DailyDietPlan` que agrupa `Diet` entries.
        "user": user.id,
        "date": timezone.now().date(),
        "target_calories": calories_target,
        "target_protein": total_target_protein,
        "target_carbs": total_target_carbs,
        "target_fat": total_target_fat,
        "water_intake_ml": 2000,
        "suggested_meals": generated_diets,  # lista de instâncias Diet
        "macro_distribution_percentage": {
            'protein': round((total_generated_protein * 4 / (total_generated_calories if total_generated_calories > 0 else 1)) * 100),
            'carbs': round((total_generated_carbs * 4 / (total_generated_calories if total_generated_calories > 0 else 1)) * 100),
            'fat': round((total_generated_fat * 9 / (total_generated_calories if total_generated_calories > 0 else 1)) * 100),
        },
        "rating": None,
        "created_at": timezone.now(),
        "updated_at": timezone.now(),
    }

    obj = SimpleNamespace(**response_data)
    return Response(DailyDietPlanSerializer(obj).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_diet(request):
    serializer = DietSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({'detail': 'Dieta registrada com sucesso!', 'diet': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)