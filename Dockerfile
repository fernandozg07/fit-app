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
ENV PORT=8000

# Create staticfiles directory
RUN mkdir -p /app/staticfiles

# Expose port
EXPOSE $PORT

# Create startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Run startup script
CMD ["/bin/bash", "/app/start.sh"]