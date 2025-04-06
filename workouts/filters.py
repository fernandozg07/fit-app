from django_filters import rest_framework as filters
from .models import Workout

class WorkoutFilter(filters.FilterSet):
    carga__gte = filters.NumberFilter(field_name="carga", lookup_expr="gte")
    carga__lte = filters.NumberFilter(field_name="carga", lookup_expr="lte")
    duration__gte = filters.DurationFilter(field_name="duration", lookup_expr="gte")
    duration__lte = filters.DurationFilter(field_name="duration", lookup_expr="lte")

    class Meta:
        model = Workout
        fields = ['workout_type', 'intensity', 'frequency', 'carga', 'duration']
