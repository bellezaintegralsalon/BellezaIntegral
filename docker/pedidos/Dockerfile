# Servicio "pedidos": misma base de código de Belleza Integral.
# La variable SERVICE hace que este contenedor exponga solo su dominio de rutas.
#
# Construir desde la RAÍZ del repo:
#   docker build -f docker/pedidos/Dockerfile -t belleza-pedidos .

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SERVICE=pedidos \
    HOST=0.0.0.0 \
    PORT=5000

WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts
COPY database ./database
COPY start_server.py wsgi.py ./

RUN useradd --create-home appuser
USER appuser

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/api/v1/health')" || exit 1

CMD ["python", "start_server.py"]
