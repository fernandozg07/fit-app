#!/bin/bash

# Script de inicialização para Railway

echo "🚀 Iniciando aplicação Fitness App..."

# Executa migrações
echo "📦 Executando migrações do banco de dados..."
python manage.py migrate --noinput

# Coleta arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Cria superusuário se não existir
echo "👤 Verificando superusuário..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@fitness.com', 'admin123')
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
"

# Inicia o servidor
echo "🌐 Iniciando servidor..."
gunicorn fitness_app.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120