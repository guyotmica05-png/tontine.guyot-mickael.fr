FROM python:3.11-slim-bookworm

# Dependances systeme requises par WeasyPrint (rendu HTML/CSS -> PDF, 100% local)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu-core \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

# Aucun volume, aucune ecriture disque : tout est genere en memoire (io.BytesIO)
# et streame directement dans la reponse HTTP.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
