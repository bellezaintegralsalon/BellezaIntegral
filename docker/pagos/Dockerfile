# Servicio "pagos": microservicio nuevo, independiente del resto (sin base de datos).
#
# Construir desde la RAÍZ del repo:
#   docker build -f docker/pagos/Dockerfile -t belleza-pagos .

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/srv

WORKDIR /srv

COPY src/pagos/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/pagos ./pagos

RUN useradd --create-home appuser
USER appuser

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/api/v1/health')" || exit 1

CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "--call", "pagos.app:create_app"]
