"""Microservicio de pagos (DEVOPS 1): esqueleto SIN base de datos.

El checkout real de Belleza Integral ya vive en /pedidos (tienda_routes.py) y
en /suscripciones (pagos_suscripcion), ambos sobre MySQL. Este servicio no
sustituye esa lógica ni toca el esquema de la base: solo demuestra un dominio
de "pagos" separado, con una simulación de aprobación en memoria.
"""
import uuid

from flask import Flask, jsonify, request


def _respuesta(ok, mensaje, datos=None, codigo=200):
    return jsonify({"success": ok, "message": mensaje, "data": datos}), codigo


def create_app():
    app = Flask(__name__)
    app.json.ensure_ascii = False

    @app.get("/api/v1/health")
    def health():
        return _respuesta(True, "Servicio de pagos disponible", {"servicio": "pagos"})

    @app.post("/api/v1/pagos")
    def simular_pago():
        cuerpo = request.get_json(silent=True) or {}
        try:
            pedido_id = int(cuerpo["pedido_id"])
            monto = round(float(cuerpo["monto"]), 2)
            if pedido_id <= 0 or monto <= 0:
                raise ValueError
        except (KeyError, TypeError, ValueError):
            return _respuesta(False, "pedido_id y monto deben ser números positivos.", None, 400)
        return _respuesta(True, "Pago simulado aprobado (no se guarda en ninguna base de datos)", {
            "pedido_id": pedido_id,
            "monto": monto,
            "estado": "simulado_aprobado",
            "referencia": uuid.uuid4().hex,
        }, 201)

    return app
