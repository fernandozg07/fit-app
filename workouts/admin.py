from django.contrib import admin
from .models import Workout, WorkoutLog, WorkoutFeedback
    

admin.site.register(Workout)
admin.site.register(WorkoutLog)
admin.site.register(WorkoutFeedback)
