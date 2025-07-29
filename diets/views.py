import datetime
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

            # Passar a instância diretamente, não o .data
            daily_plans_grouped[date_key]['suggested_meals'].append(diet_entry)
            daily_plans_grouped[date_key]['total_calories'] += diet_entry.calories
            daily_plans_grouped[date_key]['total_protein'] += diet_entry.protein
            daily_plans_grouped[date_key]['total_carbs'] += diet_entry.carbs
            daily_plans_grouped[date_key]['total_fat'] += diet_entry.fat

            feedbacks = DietFeedback.objects.filter(diet=diet_entry)
            for feedback in feedbacks:
                daily_plans_grouped[date_key]['ratings'].append(feedback.rating)

        final_daily_plans = []
        for date_key, data in daily_plans_grouped.items():
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

    if meals_count > 0 and calories_target:
        calories_per_meal = calories_target / meals_count
        protein_per_meal = (calories_target * 0.3 / 4) / meals_count
        carbs_per_meal = (calories_target * 0.4 / 4) / meals_count
        fat_per_meal = (calories_target * 0.3 / 9) / meals_count
    else:
        calories_per_meal = protein_per_meal = carbs_per_meal = fat_per_meal = 0

    meal_types_available = [choice[0] for choice in MEAL_CHOICES]

    for i in range(meals_count):
        meal_type = meal_types_available[i % len(meal_types_available)]

        meal_name = f"Refeição de {meal_type.replace('_', ' ').capitalize()}"
        meal_description = f"Uma opção saudável e balanceada para o {meal_type.replace('_', ' ').lower()}, focada em seu objetivo de {goal.replace('_', ' ')}."
        meal_ingredients = [f"Ingrediente A {i+1}", f"Ingrediente B {i+1}", f"Ingrediente C {i+1}"]
        meal_preparation_time = 20 + (i * 5)

        diet_entry = Diet.objects.create(
            user=user,
            meal=meal_type,
            calories=round(calories_per_meal, 2),
            protein=round(protein_per_meal, 2),
            carbs=round(carbs_per_meal, 2),
            fat=round(fat_per_meal, 2),
            name=meal_name,
            description=meal_description,
            ingredients=meal_ingredients,
            preparation_time_minutes=meal_preparation_time,
            goal=goal,
            dietary_restrictions=dietary_restrictions,
            preferred_cuisine=preferred_cuisine,
            target_calories=calories_target,
            target_protein=round(calories_target * 0.3 / 4) if calories_target else 0,
            target_carbs=round(calories_target * 0.4 / 4) if calories_target else 0,
            target_fat=round(calories_target * 0.3 / 9) if calories_target else 0,
            water_intake_ml=2000,
            rating=None,
        )
        generated_diets.append(diet_entry)

    total_generated_calories = sum(d.calories for d in generated_diets)
    total_generated_protein = sum(d.protein for d in generated_diets)
    total_generated_carbs = sum(d.carbs for d in generated_diets)
    total_generated_fat = sum(d.fat for d in generated_diets)

    response_data = {
        "id": generated_diets[0].id if generated_diets else None,
        "user": user.id,
        "date": timezone.now().date(),
        "target_calories": calories_target,
        "target_protein": round(calories_target * 0.3 / 4) if calories_target else 0,
        "target_carbs": round(calories_target * 0.4 / 4) if calories_target else 0,
        "target_fat": round(calories_target * 0.3 / 9) if calories_target else 0,
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
