#!/bin/bash
set -e

echo "🚀 Iniciando Fitness App..."

# Migrações
echo "📦 Executando migrações..."
python manage.py migrate --noinput || echo "Migrações falharam, continuando..."

# Arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput || echo "Collectstatic falhou, continuando..."

# Servidor
echo "🌐 Iniciando servidor na porta $PORT..."
exec gunicorn fitness_app.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -