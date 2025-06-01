FROM python:3.12-slim

WORKDIR /app

# Installation des dépendances système minimales
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des requirements d'abord pour mieux utiliser le cache Docker
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie du reste de l'application
COPY . .

# Commande par défaut (à adapter selon votre framework)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]