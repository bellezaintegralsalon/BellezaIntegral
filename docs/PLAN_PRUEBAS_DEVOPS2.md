# Plan de pruebas de Belleza Integral para DEVOPS 2

## Propósito y objetivos

Este plan valida el incremento de servicios, disponibilidad y citas antes de su
publicación en staging. Conserva la regresión existente de pedidos, inventario,
suscripciones, puntos y reportes para detectar efectos de los cambios.

El objetivo general es comprobar que el cliente puede gestionar una cita y que
la aplicación respeta autenticación, roles, propiedad e integridad de agenda.
Los objetivos específicos son rechazar horarios ocupados, conservar reservas
ante cambios fallidos, liberar intervalos cancelados y generar evidencia
reproducible mediante pytest y Selenium.

## Alcance

Se cubren registro e ingreso de clientes, permisos, catálogo de servicios,
disponibilidad, reservas, concurrencia, reprogramación, cancelación y sesión
desde la interfaz. La aceptación con el negocio y la revisión manual de UX
son actividades separadas de la aprobación automática.

No se evalúan pagos bancarios reales, envío externo de notificaciones ni
continuidad de ocho horas. Los pagos del proyecto son simulados. Las pruebas
de concurrencia locales no acreditan un SLA del despliegue en Railway.

El esquema CI es el mínimo de tests/sql/001_esquema_ci.sql, las tablas de
auditoría y la migración 008 disponible. No reproduce los 40 triggers y las
10 rutinas de una instalación institucional completa. La comprobación
/health/schema corresponde al ambiente que tenga esas migraciones instaladas.

## Tipos y estrategia

| Tipo | Cobertura | Ejecución |
|---|---|---|
| Unitarias | Validadores y reglas sin MySQL | pytest tests/unit |
| Integración | API y persistencia MySQL; concurrencia real | pytest con base aislada |
| Sistema | Login, reserva, reprogramación y cancelación en la web | pytest y Selenium Chrome |
| Aceptación | Criterios y conformidad del salón | Manual con representante del negocio |
| Seguridad | Token, rol, propiedad y revocación | pytest y comprobaciones de interfaz |
| Rendimiento | Veinte consultas concurrentes locales | pytest; medición HTTP adicional en staging |
| UX | Mensajes, navegación, teclado y adaptación visual | Manual en escritorio y móvil |

## Ambiente y datos

La aplicación utiliza Python, Flask, SQLAlchemy, PyMySQL y MySQL. Cada ejecución
guarda las versiones efectivas, sistema operativo, arquitectura, recursos
visibles, commit y estado de cambios en artifacts/entorno.json. Selenium guarda
la versión real del navegador como propiedad JUnit. Registrar por separado los
recursos asignados en Railway; los recursos visibles del equipo de CI no los
sustituyen.

Las cuentas cuenta1 a cuenta6@example.com son ficticias. El fixture contiene
administradores, clientes y personal; usa PasswordTest2026! solo como dato de
prueba. Las fechas se calculan en America/Guatemala y las reservas se sitúan
siete días después para evitar dependencia de una fecha fija.

La base debe terminar en _test. La preparación se detiene si encuentra tablas
sin belleza_test_marker. Los fixtures limpian sus tablas antes de cada caso:
nunca apuntar a producción ni a una base del salón.

## Criterios y responsabilidades

Entrada: código identificado, Python y dependencias disponibles, esquema
aislado preparado y navegador/controlador compatibles para Selenium.
Salida: todas las pruebas obligatorias ejecutadas y aprobadas, sin omisiones;
ningún defecto crítico o alto que bloquee reservas; aceptación y UX registradas
antes de declarar completo el incremento. Un resultado skipped es no ejecutado.

El equipo de desarrollo mantiene código y pruebas. El responsable de la
ejecución registra versión, fecha y evidencias. El Product Owner o representante
del salón valida los criterios de negocio. Confirmar la distribución de tareas
entre Luis, Gerizim y Lilian en el backlog real del Sprint 2.

## Ejecución y reportes

```bash
python -m pip install -r requirements-test.txt
python scripts/preparar_bd_pruebas.py
python scripts/ejecutar_pruebas.py --suite todas
```

Antes de preparar o ejecutar integración, configurar BELLEZA_TEST_DATABASE_URL
solo para la base aislada. Para unitarias sin MySQL:

```bash
python scripts/ejecutar_pruebas.py --suite unitarias
```

El ejecutor separa unitarias, integración y Selenium. Genera HTML autónomo,
JUnit XML, contexto y JSON de resultados por ID. Los errores y omisiones devuelven
un estado distinto de cero. Jenkins y GitHub Actions archivan los artefactos
aunque el flujo falle. Las capturas Selenium muestran la interfaz real; no son
pruebas manuales de UX ni una aceptación del negocio.

## Casos y trazabilidad

Los 22 casos completos se conservan en casos_prueba_devops2.json y en el Word
del plan. La ficha sigue Campo / Contenido y la tabla No. / Acción / Resultado
esperado del documento Proyecto Final Fase I. Cada caso tiene resultado obtenido,
estado y referencia de automatización. Asociar la columna de escenario con los
IDs reales de HU/RF en Azure Boards; no reutilizar los RF de Task Management.

Los marcadores @pytest.mark.caso conectan CP-01 a CP-20 con JUnit. CP-02 contiene
cuatro variantes, por lo que el número de pruebas pytest y el número de casos
documentados son diferentes. CP-21 y CP-22 requieren revisión manual.

## Defectos y rendimiento

Registrar DEF, CP/HU relacionado, severidad, prioridad, ambiente, pasos,
esperado, obtenido y evidencia. Una diferencia contra el resultado esperado es
fallida, aunque otros pasos funcionen. Clasificar por separado los errores de
automatización y los defectos de aplicación.

Para rendimiento en staging, acordar antes la cantidad de clientes, duración,
tasa de solicitudes y umbral p95. Medir HTTP contra una base de pruebas,
registrar errores y latencias. El caso CP-18 solo comprueba concurrencia local.

## Referencias

- Repositorio: https://github.com/bellezaintegralsalon/BellezaIntegral
- pytest HTML: https://pytest-html.readthedocs.io/en/latest/user_guide.html
- Selenium: https://www.selenium.dev/documentation/webdriver/
- Jenkins: https://www.jenkins.io/doc/book/pipeline/jenkinsfile/
- Railway: https://docs.railway.com/cli/up
