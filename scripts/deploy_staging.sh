#!/usr/bin/env bash
# Requiere Railway CLI instalado y un token limitado al ambiente staging.
set -euo pipefail
: "${RAILWAY_TOKEN:?Configurar token de staging en el gestor de credenciales}"
: "${RAILWAY_PROJECT_ID:?Falta proyecto Railway}"
: "${RAILWAY_SERVICE_ID:?Falta servicio de staging}"
: "${STAGING_URL:?Falta URL HTTPS de staging}"
case "$STAGING_URL" in https://*) ;; *) echo 'La URL de staging debe usar HTTPS'; exit 1;; esac
command -v railway >/dev/null
command -v curl >/dev/null
mkdir -p artifacts
# El modo adjunto espera el despliegue. No crea dominios ni ambientes.
railway up --project "$RAILWAY_PROJECT_ID" --environment staging --service "$RAILWAY_SERVICE_ID"
ok=0
for intento in $(seq 1 30); do
  if curl --fail --silent --show-error --max-time 10 \
      "${STAGING_URL%/}/api/v1/health" -o artifacts/staging-health.json; then ok=1; break; fi
  sleep 2
done
if [ "$ok" != 1 ]; then echo 'Staging no respondió a la comprobación de salud'; exit 1; fi
curl --fail --silent --show-error --max-time 10 \
  "${STAGING_URL%/}/api/v1/health/db" -o artifacts/staging-db.json
git rev-parse HEAD > artifacts/staging-commit.txt
echo 'Despliegue de staging y conexión MySQL comprobados'
