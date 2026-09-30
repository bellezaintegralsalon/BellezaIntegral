# Implementación de DEVOPS 2 en Belleza Integral

## Cambios preparados

Jenkinsfile implementa Checkout, Build, Test y Deploy staging. GitHub Actions
mantiene la integración existente y añade HTML, trazabilidad y Selenium.
La promoción automática dev a main se conserva: solo se ejecuta después del
job de pruebas. Publicar esta entrega primero en una rama de revisión y abrir
un PR hacia dev evita activar producción durante la revisión.

Los reportes se archivan por ejecución; una corrida local no equivale a una
ejecución de Jenkins ni a un despliegue exitoso. Completar las capturas de Jenkins
y la evidencia de staging cuando se configuren esos servicios.

## Preparar Jenkins

1. Configurar un agente Linux con Python 3.12 y venv, Git, Bash, Docker CLI y
   acceso al daemon Docker. Registrar sus versiones efectivas.
2. Instalar los plugins Pipeline, Git, Credentials Binding y JUnit.
3. Instalar Chrome/Chromium y ChromeDriver compatibles, o permitir a Selenium
   Manager descargarlos. Puede configurarse CHROME_BINARY y CHROMEDRIVER.
4. Crear un Pipeline from SCM para la rama de revisión y ruta Jenkinsfile.
5. Ejecutar con DEPLOY_STAGING desactivado para comprobar build y pruebas.

Test crea MySQL 8.4 en un contenedor efímero con puerto aleatorio de localhost,
prepara el esquema y ejecuta las tres suites. El contenedor se elimina al
finalizar, incluso si falla. Las credenciales del contenedor son exclusivamente
de pruebas. El agente debe ser dedicado al equipo y autorizado para Docker.

## Configurar staging

1. Crear el ambiente staging y un servicio Railway separado del productivo.
2. Configurar su base MySQL de pruebas, las variables DB_HOST/DB_PORT/DB_NAME/
   DB_USER/DB_PASSWORD, JWT_SECRET_KEY y SERVICE=all. No copiar datos reales.
3. Usar el arranque existente de scripts/servir.py, respetando PORT y HOST del
   ambiente. Railway necesita HOST=0.0.0.0.
4. Preparar las migraciones de ese ambiente antes de la demostración.
5. Instalar Railway CLI en Jenkins y registrar la versión utilizada.
6. Crear la credencial Secret text railway-staging-token con un token limitado
   al ambiente staging. Nunca colocar el token en archivos ni en parámetros.
7. Completar RAILWAY_PROJECT_ID, RAILWAY_SERVICE_ID y STAGING_URL y activar
   DEPLOY_STAGING. El comando usa explícitamente --environment staging.

El despliegue espera el resultado de Railway y después verifica /api/v1/health
y /api/v1/health/db. Guardar logs, URL, commit y captura del ambiente. La presencia
de Jenkinsfile sin ejecutar esta etapa no acredita un CI/CD funcional completo.

## Evidencias y orden de entrega

- Conservar una ejecución fallida real y su diagnóstico; luego la corregida.
- Mostrar resultados unitarios, integración, Selenium y los reportes HTML.
- Mostrar el despliegue de staging y la comprobación de conexión MySQL.
- Documentar CP-21 UX y CP-22 aceptación con responsables y fecha.
- Completar Scrum con datos reales del Sprint 2; usar SCRUM_SPRINT2.md.
- Grabar el video con GUION_VIDEO_DEVOPS2.md y sus evidencias reales.

El README anterior describe un PR automático, pero el job promote realiza
fast-forward y push directo. El README de esta entrega se ajusta a ese mecanismo.

## Referencias oficiales

- https://www.jenkins.io/doc/book/pipeline/syntax/
- https://www.jenkins.io/doc/pipeline/tour/tests-and-artifacts/
- https://docs.railway.com/cli/up
- https://docs.railway.com/environments
