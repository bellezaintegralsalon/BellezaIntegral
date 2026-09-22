"""Pruebas del microservicio de pagos (src/pagos), independientes del resto."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_pagos_health():
    from pagos.app import create_app
    r = create_app().test_client().get("/api/v1/health")
    assert r.status_code == 200
    assert r.get_json()["success"] is True


def test_pagos_simulado_aprobado():
    from pagos.app import create_app
    r = create_app().test_client().post("/api/v1/pagos", json={"pedido_id": 1, "monto": 50})
    assert r.status_code == 201
    assert r.get_json()["data"]["estado"] == "simulado_aprobado"


def test_pagos_rechaza_monto_invalido():
    from pagos.app import create_app
    r = create_app().test_client().post("/api/v1/pagos", json={"pedido_id": 1, "monto": 0})
    assert r.status_code == 400
