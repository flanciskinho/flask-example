FROM python:3.14-slim

# Evita archivos .pyc y activa stdout inmediato
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código de la app
COPY . .

# Puerto interno
EXPOSE 8000

# Levantar la applicacion
CMD ["gunicorn", "--log-level=info", "--logger-class", "gunicorn.glogging.Logger", "--bind", "0.0.0.0:8000", "wsgi:app"]
