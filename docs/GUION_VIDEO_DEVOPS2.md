# Guion del video DEVOPS 2 de Belleza Integral

Duración prevista 9 minutos y 30 segundos. Repartir las intervenciones entre
Luis, Gerizim y Lilian según el trabajo real de cada integrante. Reemplazar las
menciones de staging por evidencia de una ejecución real antes de grabar.

| Tiempo | Pantalla y demostración | Narración sugerida |
|---|---|---|
| 0:00 a 0:45 | Portada y aplicación | Presentamos Belleza Integral y el incremento de servicios, disponibilidad y citas. Vamos a mostrar cómo validamos un cambio antes de llevarlo al ambiente de pruebas. |
| 0:45 a 1:30 | Repositorio y ramas | El código se revisa por rama y commit. El ambiente staging tiene su servicio y base separados de producción. |
| 1:30 a 3:00 | Jenkinsfile y ejecución Jenkins | Checkout obtiene el código. Build prepara Python y valida dependencias. Test ejecuta unitarias, MySQL y navegador. Deploy staging solo continúa si los resultados lo permiten. |
| 3:00 a 4:00 | Ejecución fallida y posterior corregida | Mostramos el error real, explicamos su causa y el cambio que permitió pasar las pruebas. La publicación se detiene cuando falla una etapa obligatoria. |
| 4:00 a 4:45 | Railway staging y comprobación de salud | Este es el servicio de pruebas. Comprobamos la API y la conexión con MySQL después del despliegue. |
| 4:45 a 6:00 | Plan Word y casos | El plan contiene objetivos, alcance, tipos, datos y criterios. Cada caso identifica precondiciones, acciones, esperado, obtenido y evidencia. |
| 6:00 a 7:00 | Reportes HTML | Aquí se observa el resultado de pytest y su relación con los IDs. Las omisiones se registran como no ejecutadas. |
| 7:00 a 8:00 | Selenium y capturas | El navegador inicia sesión, reserva, reprograma y cancela una cita mediante la interfaz real. La revisión manual de UX complementa la automatización. |
| 8:00 a 9:00 | Backlog y Scrum | Mostramos tareas, responsables, trabajo pendiente por día y los acuerdos reales del Sprint 2. |
| 9:00 a 9:30 | Resultado y pendientes | Indicamos cuántas pruebas pasaron, qué aceptó el negocio y qué observaciones continúan en el backlog. |

Evitar mostrar tokens, contraseñas o datos de clientes. Una ejecución local
puede demostrarse como local; no nombrarla como Jenkins o Railway.
