# Utilise une image Python officielle comme base
FROM python:3.12.5-slim

# Définit le répertoire de travail
WORKDIR /app

# Copie les fichiers de dépendances
COPY requirements.txt .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie le reste des fichiers du projet
COPY . .

# Commande à exécuter au lancement du conteneur
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "votre_projet.wsgi:application"]