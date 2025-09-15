#!/bin/bash

# Define porta padrão
PORT=${PORT:-8000}

echo "Iniciando na porta $PORT..."

# Aguarda PostgreSQL ficar disponível
echo "Aguardando PostgreSQL..."
until pg_isready -h postgres.railway.internal -p 5432 -U postgres; do
  echo "PostgreSQL não está pronto - aguardando..."
  sleep 2
done
echo "PostgreSQL está pronto!"

# Migrações
echo "Executando migrações..."
python manage.py migrate --noinput

# Arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Servidor
echo "Iniciando servidor..."
exec gunicorn fitness_app.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120