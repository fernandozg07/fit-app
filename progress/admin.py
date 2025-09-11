# progress/admin.py
from django.contrib import admin
from .models import ProgressEntry  # Corrija para ProgressEntry, não Progress

admin.site.register(ProgressEntry)  # Registra o modelo no admin
#dw