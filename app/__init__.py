import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify

from .database import crear_motor
from .routes import api
from .auth_routes import auth
from .security import configurar_jwt
from .admin_routes import admin
from .servicios_routes import servicios
from .personal_routes import personal
from .disponibilidad_routes import disponibilidad
from .citas_routes import citas
from .agenda_routes import agenda

# DEVOPS 1: cada contenedor puede exponer solo un dominio de la API mediante
# la variable de entorno SERVICE. Si SERVICE no está definida (o vale "all"),
# el comportamiento es EXACTAMENTE el mismo de siempre: se registran todos
# los blueprints. Esto es lo que ocurre hoy en Railway, porque esa variable
# no existe ahí.
GRUPOS_SERVICIO = {
    "auth": {"auth", "admin", "cuentas", "auditoria", "reportes", "visor"},
    "catalogo": {"servicios", "personal", "disponibilidad", "horarios", "citas", "agenda"},
    "pedidos": {"tienda", "fidelizacion", "suscripciones"},
}


def _blueprints_activos():
    servicio = os.getenv("SERVICE", "all").strip().lower()
    if servicio in ("", "all"):
        return None
    if servicio not in GRUPOS_SERVICIO:
        raise RuntimeError("SERVICE debe ser: all, " + ", ".join(GRUPOS_SERVICIO) + ".")
    return GRUPOS_SERVICIO[servicio]


def create_app():
    raiz = Path(__file__).resolve().parent.parent
    load_dotenv(raiz / ".env")

    activos = _blueprints_activos()

    def registrar(app, blueprint):
        if blueprint.name == "api" or activos is None or blueprint.name in activos:
            app.register_blueprint(blueprint)

    app = Flask(__name__)
    app.json.ensure_ascii = False
    configurar_jwt(app)
    app.extensions["db_engine"] = crear_motor()
    for blueprint in (api, auth, admin, servicios, personal, disponibilidad, citas, agenda):
        registrar(app, blueprint)

    @app.errorhandler(404)
    def ruta_no_encontrada(error):
        return jsonify({
            "success": False,
            "message": "Ruta no encontrada",
            "data": None
        }), 404

    from .tienda_routes import tienda
    from .fidelizacion_routes import fidelizacion
    from .cuentas_routes import cuentas
    from .horarios_routes import horarios
    from .reportes_routes import reportes
    from .visor_routes import visor
    from .auditoria_routes import auditoria
    from .suscripciones_routes import suscripciones
    from .integracion import configurar_integracion
    for blueprint in (tienda, fidelizacion, cuentas, horarios, reportes, visor, auditoria, suscripciones):
        registrar(app, blueprint)
    configurar_integracion(app)
    return app
