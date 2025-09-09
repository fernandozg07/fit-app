import datetime
import random
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
    """
    Ajusta as calorias de uma dieta com base na avaliação recebida.
    Aumenta calorias se a avaliação for alta (>=4), diminui se for baixa (<=2).
    """
    if rating >= 4:
        diet.calories += 100
    elif rating <= 2:
        diet.calories = max(1200, diet.calories - 100) # Garante um mínimo de 1200 kcal
    diet.save()

class DietViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD em Dietas.
    Permite listar, criar, recuperar, atualizar e deletar dietas.
    """
    queryset = Diet.objects.all()
    serializer_class = DietSerializer
    permission_classes = [IsAuthenticated] # Apenas usuários autenticados podem acessar
    filter_backends = [DjangoFilterBackend] # Habilita filtragem
    filterset_class = DietFilter # Define a classe de filtro

    def perform_create(self, serializer):
        """
        Associa o usuário logado à dieta ao criá-la.
        """
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
        Retorna apenas as dietas do usuário logado, ordenadas por data e tipo de refeição.
        """
        if self.request.user.is_authenticated:
            return Diet.objects.filter(user=self.request.user).order_by('-date', 'meal')
        return Diet.objects.none() # Retorna queryset vazio se o usuário não estiver autenticado

    def list(self, request, *args, **kwargs):
        """
        Lista os planos de dieta diários, agrupando as refeições por data.
        Calcula totais de calorias/macros e percentuais de distribuição.
        """
        user = request.user
        user_diets = self.get_queryset()

        # Usa defaultdict para agrupar as refeições por data
        daily_plans_grouped = defaultdict(lambda: {
            'suggested_meals': [],
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fat': 0,
            'ratings': [],
            'id': None, # Será o ID da primeira refeição do dia (workaround para ID do plano)
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
            date_key = diet_entry.date.isoformat() # Chave para agrupar por data

            # Inicializa os metadados do plano diário com base na primeira refeição encontrada para aquela data
            if daily_plans_grouped[date_key]['id'] is None:
                daily_plans_grouped[date_key]['id'] = diet_entry.id
                daily_plans_grouped[date_key]['created_at'] = diet_entry.created_at
                daily_plans_grouped[date_key]['updated_at'] = diet_entry.updated_at
                daily_plans_grouped[date_key]['target_calories'] = diet_entry.target_calories
                daily_plans_grouped[date_key]['target_protein'] = diet_entry.target_protein
                daily_plans_grouped[date_key]['target_carbs'] = diet_entry.target_carbs
                daily_plans_grouped[date_key]['target_fat'] = diet_entry.target_fat
                daily_plans_grouped[date_key]['water_intake_ml'] = diet_entry.water_intake_ml
                daily_plans_grouped[date_key]['actual_date_obj'] = diet_entry.date

            # Adiciona a refeição à lista de refeições sugeridas para aquele dia
            daily_plans_grouped[date_key]['suggested_meals'].append(diet_entry)
            # Soma os totais de calorias e macros
            daily_plans_grouped[date_key]['total_calories'] += diet_entry.calories
            daily_plans_grouped[date_key]['total_protein'] += diet_entry.protein
            daily_plans_grouped[date_key]['total_carbs'] += diet_entry.carbs
            daily_plans_grouped[date_key]['total_fat'] += diet_entry.fat

            # Coleta feedbacks para calcular a avaliação média do dia
            feedbacks = DietFeedback.objects.filter(diet=diet_entry)
            for feedback in feedbacks:
                daily_plans_grouped[date_key]['ratings'].append(feedback.rating)

        final_daily_plans = []
        # Ordena os planos diários por data em ordem decrescente
        sorted_dates = sorted(daily_plans_grouped.keys(), reverse=True)
        
        for date_key in sorted_dates:
            data = daily_plans_grouped[date_key]
            # Calcula a avaliação média do dia
            avg_rating = sum(data['ratings']) / len(data['ratings']) if data['ratings'] else None
            plan_date = data['actual_date_obj'] or timezone.now().date()
            # Garante que total_calories_for_macros não seja zero para evitar divisão por zero
            total_calories_for_macros = data['total_calories'] if data['total_calories'] > 0 else 1

            # Monta os dados do plano diário
            daily_plan_data = {
                'id': data['id'],
                'user': data['user'],
                'date': plan_date,
                'target_calories': data['target_calories'],
                'target_protein': data['target_protein'],
                'target_carbs': data['target_carbs'],
                'target_fat': data['target_fat'],
                'water_intake_ml': data['water_intake_ml'],
                'suggested_meals': data['suggested_meals'],  # Lista de instâncias Diet
                'macro_distribution_percentage': {
                    'protein': round((data['total_protein'] * 4 / total_calories_for_macros) * 100),
                    'carbs': round((data['total_carbs'] * 4 / total_calories_for_macros) * 100),
                    'fat': round((data['total_fat'] * 9 / total_calories_for_macros) * 100),
                },
                'rating': avg_rating,
                'created_at': data['created_at'],
                'updated_at': data['updated_at'],
            }
            # Usa SimpleNamespace para criar um objeto que pode ser serializado
            obj = SimpleNamespace(**daily_plan_data)
            final_daily_plans.append(DailyDietPlanSerializer(obj).data)

        return Response(final_daily_plans, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_diet(request):
    """
    Gera um plano de dieta com base nos objetivos e preferências do usuário.
    Distribui calorias e macronutrientes de forma mais inteligente entre as refeições
    e sugere nomes, descrições e ingredientes variados.
    """
    user = request.user
    serializer = DietGenerateInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    goal = serializer.validated_data.get('goal')
    calories_target = serializer.validated_data.get('calories_target')
    meals_count = serializer.validated_data.get('meals_count')
    dietary_restrictions = serializer.validated_data.get('dietary_restrictions', [])
    preferred_cuisine = serializer.validated_data.get('preferred_cuisine')

    generated_diets = []

    # Mapeamento de proporções de calorias *relativas* por tipo de refeição.
    # Estas proporções serão usadas para distribuir o total de calorias diárias.
    # A soma dessas proporções para os tipos de refeição selecionados será normalizada para 1.0.
    meal_relative_calorie_proportions = {
        'breakfast': 0.25, # Ex: Café da manhã contribui com 25% das calorias diárias
        'lunch': 0.40,     # Almoço contribui com 40%
        'dinner': 0.35,    # Jantar contribui com 35%
        'snack': 0.10,     # Lanche contribui com 10%
        'afternoon_snack': 0.10,
        'pre_workout': 0.05,
        'post_workout': 0.05,
    }

    # Mapeamento de proporções de macronutrientes (proteína, carboidratos, gordura)
    # *dentro* da caloria de CADA refeição. A soma de protein_ratio, carbs_ratio, fat_ratio deve ser 1.0 (100%).
    meal_macro_ratios = {
        'breakfast': {'protein_ratio': 0.25, 'carbs_ratio': 0.50, 'fat_ratio': 0.25},
        'lunch': {'protein_ratio': 0.35, 'carbs_ratio': 0.40, 'fat_ratio': 0.25},
        'dinner': {'protein_ratio': 0.40, 'carbs_ratio': 0.30, 'fat_ratio': 0.30},
        'snack': {'protein_ratio': 0.30, 'carbs_ratio': 0.40, 'fat_ratio': 0.30},
        'afternoon_snack': {'protein_ratio': 0.30, 'carbs_ratio': 0.40, 'fat_ratio': 0.30},
        'pre_workout': {'protein_ratio': 0.20, 'carbs_ratio': 0.60, 'fat_ratio': 0.20},
        'post_workout': {'protein_ratio': 0.40, 'carbs_ratio': 0.40, 'fat_ratio': 0.20},
    }
    
    # Mapeamento de conteúdo de refeições (nomes, descrições, ingredientes)
    # Cada lista interna corresponde a uma opção completa de refeição para aquele tipo.
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
        'afternoon_snack': { 
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

    selected_meal_types = []
    available_choices = [choice[0] for choice in MEAL_CHOICES] # Obtém apenas os códigos dos tipos de refeição
    random.shuffle(available_choices) # Embaralha todos os tipos de refeição disponíveis

    # Prioriza a seleção de refeições principais (café, almoço, jantar)
    priority_meals_order = ['breakfast', 'lunch', 'dinner', 'snack', 'afternoon_snack', 'pre_workout', 'post_workout']
    
    for meal_code in priority_meals_order:
        if meal_code in available_choices and meal_code not in selected_meal_types:
            selected_meal_types.append(meal_code)
            if len(selected_meal_types) == meals_count:
                break
    
    # Se ainda precisar de mais refeições, adiciona as restantes que não foram selecionadas
    while len(selected_meal_types) < meals_count and available_choices:
        next_meal = available_choices.pop(0)
        if next_meal not in selected_meal_types:
            selected_meal_types.append(next_meal)

    # Se ainda não atingiu o número de refeições desejado (ex: meals_count > total de tipos únicos), repete alguns
    while len(selected_meal_types) < meals_count:
        selected_meal_types.append(random.choice([choice[0] for choice in MEAL_CHOICES]))

    # Calcula a soma total das proporções de calorias para as refeições selecionadas.
    # Isso é crucial para normalizar e distribuir as calorias e macros totais corretamente.
    current_selected_proportions_sum = sum(meal_relative_calorie_proportions.get(mt, 0) for mt in selected_meal_types)

    # Fallback para evitar divisão por zero se a soma das proporções for zero
    if current_selected_proportions_sum == 0:
        current_selected_proportions_sum = 1.0 # Isso fará com que as calorias sejam distribuídas igualmente

    # Calcula os alvos totais de macronutrientes com base nas calorias alvo diárias
    total_target_protein = round(calories_target * 0.3 / 4) if calories_target else 0
    total_target_carbs = round(calories_target * 0.4 / 4) if calories_target else 0
    total_target_fat = round(calories_target * 0.3 / 9) if calories_target else 0

    for meal_type in selected_meal_types:
        # Obtém a proporção de calorias relativa para este tipo de refeição
        relative_pct = meal_relative_calorie_proportions.get(meal_type, 0)
        
        # Calcula as calorias reais para esta refeição, normalizadas pela soma das proporções selecionadas.
        # Isso garante que a soma das calorias de todas as refeições geradas seja igual a calories_target.
        if current_selected_proportions_sum > 0:
            meal_calories = (calories_target * relative_pct) / current_selected_proportions_sum
        else:
            meal_calories = calories_target / meals_count # Fallback para distribuição igual se proporções não definidas

        # Obtém as proporções de macros para este tipo de refeição
        macro_ratios = meal_macro_ratios.get(meal_type, {
            'protein_ratio': 0.30, 'carbs_ratio': 0.40, 'fat_ratio': 0.30
        })

        # Calcula os macronutrientes para esta refeição com base nas calorias alocadas e proporções de macros
        meal_protein = (meal_calories * macro_ratios['protein_ratio']) / 4
        meal_carbs = (meal_calories * macro_ratios['carbs_ratio']) / 4
        meal_fat = (meal_calories * macro_ratios['fat_ratio']) / 9

        # Obtém as opções de conteúdo descritivo para a refeição
        content_options = meal_content_suggestions.get(meal_type, {
            'names': [f"Refeição {meal_type.replace('_', ' ').capitalize()}"],
            'descriptions': [f"Uma refeição de {round(meal_calories, 2)} kcal para {meal_type.replace('_', ' ').lower()}."],
            'ingredients': [["Ingredientes genéricos para", meal_type]]
        })

        # Seleciona um conjunto coerente de nome, descrição e ingredientes usando um índice aleatório
        if content_options['names'] and content_options['descriptions'] and content_options['ingredients']:
            choice_index = random.randrange(len(content_options['names']))
            meal_name = content_options['names'][choice_index]
            meal_description = content_options['descriptions'][choice_index]
            meal_ingredients = content_options['ingredients'][choice_index]
        else: # Fallback se não houver conteúdo definido para o tipo de refeição
            meal_name = f"Refeição {meal_type.replace('_', ' ').capitalize()}"
            meal_description = f"Uma refeição de {round(meal_calories, 2)} kcal para {meal_type.replace('_', ' ').lower()}."
            meal_ingredients = ["Ingredientes genéricos"]
        
        # Gera um tempo de preparo aleatório mais realista
        meal_preparation_time = random.randint(15, 60) 

        # Cria a entrada da dieta no banco de dados
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
            target_calories=calories_target, # Estes são os alvos diários para o plano
            target_protein=total_target_protein,
            target_carbs=total_target_carbs,
            target_fat=total_target_fat,
            water_intake_ml=2000, # Valor fixo por enquanto, pode ser dinâmico no futuro
            rating=None,
        )
        generated_diets.append(diet_entry)

    # Calcula os totais gerados para o plano diário
    total_generated_calories = sum(d.calories for d in generated_diets)
    total_generated_protein = sum(d.protein for d in generated_diets)
    total_generated_carbs = sum(d.carbs for d in generated_diets)
    total_generated_fat = sum(d.fat for d in generated_diets)

    # Verifica se há dietas geradas para evitar erro de índice
    first_diet_id = generated_diets[0].id if generated_diets else None
    
    # Prepara os dados da resposta para o plano diário
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
        "suggested_meals": generated_diets,  # Lista de instâncias Diet
        "macro_distribution_percentage": {
            'protein': round((total_generated_protein * 4 / (total_generated_calories if total_generated_calories > 0 else 1)) * 100),
            'carbs': round((total_generated_carbs * 4 / (total_generated_calories if total_generated_calories > 0 else 1)) * 100),
            'fat': round((total_generated_fat * 9 / (total_generated_calories if total_generated_calories > 0 else 1)) * 100),
        },
        "rating": None,
        "created_at": timezone.now(),
        "updated_at": timezone.now(),
    }

    # Converte os dados da resposta para um objeto SimpleNamespace e serializa
    obj = SimpleNamespace(**response_data)
    return Response(DailyDietPlanSerializer(obj).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_diet(request):
    """
    Registra uma nova dieta no sistema.
    """
    serializer = DietSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({'detail': 'Dieta registrada com sucesso!', 'diet': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
