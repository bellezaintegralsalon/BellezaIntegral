# Belleza Integral

Sistema para un salón de belleza: API REST (Flask + MySQL), visor web, suscripciones mensuales y,
como parte de la práctica DEVOPS 1, contenedores Docker y CI/CD con GitHub Actions.

## Arquitectura local (DEVOPS 1)

| Servicio | Contenido | Puerto local |
|---|---|---|
| `auth` | login, cuentas, administración, auditoría, reportes, visor web | 5001 |
| `catalogo` | servicios, personal, disponibilidad, horarios, citas, agenda | 5002 |
| `pedidos` | tienda, promociones, puntos, suscripciones | 5003 |
| `pagos` | microservicio (pago simulado, sin base de datos) | 5004 |

`auth`, `catalogo` y `pedidos` comparten el mismo código (`app/`) y activan solo su dominio de rutas
con la variable `SERVICE`. **Sin esa variable la API funciona exactamente igual que hoy**: así es como
está desplegada en Railway (producción), que no define `SERVICE` y por lo tanto sirve todas las rutas.

## Despliegue en producción

La aplicación corre en **Railway**, conectado a la rama `main`, con la base de datos en **Aiven (MySQL)**.
Cada Pull Request se valida con GitHub Actions (`.github/workflows/CI_CD.yml`); al fusionarse `dev` en
`main`, Railway despliega automáticamente. Lo de este README (Docker, `docker-compose.yml`) es para
**desarrollo y pruebas locales**, y no reemplaza ni modifica ese despliegue.

## Requisitos

Git, Docker Desktop (con Compose) y, para correr sin Docker, Python 3.11+.

## Ejecutar con Docker (local)

```bash
cp .env.example .env      # completar JWT_SECRET_KEY y MYSQL_ROOT_PASSWORD
docker compose up --build
```

Comprobar: `http://localhost:5001/api/v1/health` (también 5002, 5003 y 5004) y
`http://localhost:5001/api/v1/health/db` (MySQL local).
Para ver el visor web completo: `docker compose --profile monolito up api` y abrir `http://localhost:5000/`.

### Sobre el esquema de la base de datos local

La carpeta `database/` de este repositorio solo contiene `008_suscripciones.sql` (los archivos
anteriores viven ya aplicados en la base de Aiven). Para que MySQL local tenga las tablas necesarias,
`docker/mysql-init/` usa el mismo esquema base que ya está probado en el pipeline de CI
(`tests/sql/001_esquema_ci.sql`) más `database/008_suscripciones.sql`. Si en el futuro se agregan los
archivos `001` a `007` completos a `database/`, deben reemplazar a `docker/mysql-init/01_esquema_base.sql`.

## Ejecutar sin Docker

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
python scripts/servir.py
```

## Pruebas

```bash
pip install -r requirements-test.txt
pytest tests/unit -v          # no necesitan base de datos
```

Las pruebas de integración requieren `BELLEZA_TEST_DATABASE_URL` apuntando a una base vacía terminada
en `_test` (borran datos: nunca usar la base real). El pipeline de CI ya las ejecuta en cada push.

## Flujo de trabajo Git y CI/CD

`main` (producción, protegida) ← `dev` (integración) ← ramas de trabajo. Cada push a `dev` ejecuta
pruebas automáticas (`build-test`); si pasan, un job (`promote`) abre y fusiona un Pull Request de
`dev` hacia `main`, y Railway despliega. Detalle completo en `.github/workflows/CI_CD.yml`.

## Documentación

- `docs/PRUEBAS.md`: plan de pruebas.
- `docs/RUTAS.md`, `docs/openapi.json`: contrato de la API.
- `README_SERVIDOR.md`: notas de despliegue en servidor.

## Seguridad

No subir `.env`, `.env.remote`, certificados ni contraseñas. Las credenciales de Aiven y la
`JWT_SECRET_KEY` de producción se configuran como variables en Railway, no en el repositorio.
