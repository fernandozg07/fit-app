from django.contrib import admin
from .models import Diet

@admin.register(Diet)
class DietAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'meal', 'calories', 'created_at')
    search_fields = ('user__email',)
    list_filter = ('meal', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
