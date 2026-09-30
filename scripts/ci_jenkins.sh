#!/usr/bin/env bash
# Contenedor MySQL efímero y puerto aleatorio; nunca usa la base de producción.
set -euo pipefail
suffix="$(printf '%s' "${BUILD_TAG:-local-$$}" | sha256sum | cut -c1-12)"
container="belleza-devops2-$suffix"
cleanup() { docker rm -f "$container" >/dev/null 2>&1 || true; }
trap cleanup EXIT
docker run --detach --rm --name "$container" \
  --publish 127.0.0.1::3306 \
  --env MYSQL_ROOT_PASSWORD=clave_ci_solo_pruebas \
  --env MYSQL_ROOT_HOST=% \
  --env MYSQL_DATABASE=belleza_integral_test mysql:8.4 >/dev/null
ready=0
for intento in $(seq 1 60); do
  if docker exec -e MYSQL_PWD=clave_ci_solo_pruebas "$container" \
    mysql -uroot -e 'SELECT 1' >/dev/null 2>&1; then ready=1; break; fi
  sleep 2
done
if [ "$ready" != 1 ]; then docker logs "$container"; exit 1; fi
port="$(docker port "$container" 3306/tcp)"
port="${port##*:}"
export BELLEZA_TEST_DATABASE_URL="mysql+pymysql://root:clave_ci_solo_pruebas@127.0.0.1:$port/belleza_integral_test?charset=utf8mb4"
export CHROME_NO_SANDBOX=1
export SERVICE=all
.venv/bin/python scripts/preparar_bd_pruebas.py
.venv/bin/python scripts/ejecutar_pruebas.py --suite todas
