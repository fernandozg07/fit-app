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

# Run migrations, collect static and start server
CMD python manage.py migrate && python manage.py collectstatic --noinput && gunicorn fitness_app.wsgi:application --bind 0.0.0.0:$PORT --workers 2