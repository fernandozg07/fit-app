#!/bin/sh

# Aplica as migrações do banco
python manage.py migrate --noinput

# Coleta arquivos estáticos
python manage.py collectstatic --noinput

# Inicia o servidor
gunicorn fitness_app.wsgi:application --bind 0.0.0.0:$PORT
