from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Diet, DietFeedback
from .serializers import DietSerializer, DietFeedbackSerializer
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
        dieta_ajustada = ajustar_dieta(diet, nota)
        serializer = DietSerializer(dieta_ajustada)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_diet(request):
    user = request.user
    objetivo = user.objetivo.lower() if hasattr(user, 'objetivo') and user.objetivo else ""

    if objetivo == 'perda de peso':
        calorias = 1600
        proteina = 120.0
    elif objetivo == 'ganho de massa muscular':
        calorias = 2500
        proteina = 150.0
    else:
        calorias = 2000
        proteina = 130.0

    dieta = Diet.objects.create(
        user=user,
        meal='lunch',
        calories=calorias,
        protein=proteina,
        carbs=250.0,
        fat=70.0
    )

    return Response({
        'detail': 'Dieta gerada com sucesso!',
        'diet': DietSerializer(dieta).data
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
