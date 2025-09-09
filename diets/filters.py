from django_filters import rest_framework as filters
from .models import Diet

class DietFilter(filters.FilterSet):
    calories__gte = filters.NumberFilter(field_name="calories", lookup_expr="gte")
    calories__lte = filters.NumberFilter(field_name="calories", lookup_expr="lte")
    protein__gte = filters.NumberFilter(field_name="protein", lookup_expr="gte")
    carbs__lte = filters.NumberFilter(field_name="carbs", lookup_expr="lte")

    class Meta:
        model = Diet
        fields = ['meal', 'date', 'calories', 'protein', 'carbs', 'fat']
