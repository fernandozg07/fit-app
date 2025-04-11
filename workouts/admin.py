from django.contrib import admin
from .models import Workout, WorkoutLog, WorkoutFeedback

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'workout_type', 'intensity', 'duration', 'carga', 'created_at')
    search_fields = ('user__email', 'workout_type')
    list_filter = ('workout_type', 'intensity', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'workout', 'nota', 'duracao', 'created_at')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

@admin.register(WorkoutFeedback)
class WorkoutFeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'workout_log', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__email',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
