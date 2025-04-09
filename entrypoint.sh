#!/bin/sh

# Aplica as migrações do banco
echo "Aplicando migrações..."
python manage.py migrate --noinput

# Cria ou atualiza o superusuário
echo "Criando ou atualizando superusuário..."
python manage.py create_superuser --noinput

# Coleta arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Inicia o servidor
echo "Iniciando o servidor..."
gunicorn fitness_app.wsgi:application --bind 0.0.0.0:$PORT
