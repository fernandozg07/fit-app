FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=fitness_app.settings
ENV PYTHONPATH=/app

# Create staticfiles directory
RUN mkdir -p /app/staticfiles

# Expose port
EXPOSE 8000

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Iniciando Fitness App..."\n\
echo "📦 Executando migrações..."\n\
python manage.py migrate --noinput || echo "Erro nas migrações, continuando..."\n\
echo "📁 Coletando arquivos estáticos..."\n\
python manage.py collectstatic --noinput || echo "Erro no collectstatic, continuando..."\n\
echo "🌐 Iniciando servidor..."\n\
gunicorn fitness_app.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120' > /app/start.sh

RUN chmod +x /app/start.sh

# Run startup script
CMD ["/app/start.sh"]