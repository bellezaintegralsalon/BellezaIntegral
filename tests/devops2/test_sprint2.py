"""Casos independientes del Sprint 2; usan únicamente el fixture MySQL aislado."""
import pytest
from sqlalchemy import text

from test_flujos import call, catalog


@pytest.mark.caso("CP-03")
def test_cp03_registrar_cliente(client, motor):
    datos = {"nombre": "Cliente QA", "email": "registro.qa@example.com", "password": "PasswordTest2026!"}
    r = client.post("/api/v1/auth/registro", json=datos)
    assert r.status_code == 201, r.get_data(as_text=True)
    with motor.connect() as c:
        usuario = c.execute(text("SELECT rol,password_hash FROM usuarios WHERE email=:email"), {"email": datos["email"]}).mappings().one()
    assert usuario["rol"] == "cliente"
    assert usuario["password_hash"] != datos["password"]


@pytest.mark.caso("CP-04")
def test_cp04_login_valido(client):
    r = client.post("/api/v1/auth/login", json={"identificador": "cuenta2@example.com", "password": "PasswordTest2026!"})
    assert r.status_code == 200
    token = r.get_json()["data"]["access_token"]
    perfil = client.get("/api/v1/auth/perfil", headers={"Authorization": "Bearer " + token})
    assert perfil.status_code == 200
    assert perfil.get_json()["data"]["id"] == 2


@pytest.mark.caso("CP-05")
def test_cp05_login_invalido(client):
    r = client.post("/api/v1/auth/login", json={"identificador": "cuenta2@example.com", "password": "Incorrecta2026!"})
    assert r.status_code == 401
    assert "access_token" not in (r.get_json().get("data") or {})


@pytest.mark.caso("CP-06")
def test_cp06_acceso_sin_token(client):
    assert client.get("/api/v1/auth/perfil").status_code == 401
    assert client.post("/api/v1/citas", json={}).status_code == 401


@pytest.mark.caso("CP-07")
def test_cp07_cliente_no_crea_servicios(client, headers, motor):
    datos = {"nombre": "Manicura QA", "categoria": "Uñas", "duracion_min": 60, "precio": "135.00"}
    assert client.post("/api/v1/servicios", headers=headers(2), json=datos).status_code == 403
    with motor.connect() as c:
        assert c.execute(text("SELECT COUNT(*) FROM servicios")).scalar_one() == 0


@pytest.mark.caso("CP-08")
def test_cp08_crear_servicio(client, headers, motor):
    datos = {"nombre": "Manicura QA", "categoria": "Uñas", "duracion_min": 60, "precio": "135.00"}
    result = call(client, headers, "/servicios", "POST", datos, expected=201)["data"]
    with motor.connect() as c:
        row = c.execute(text("SELECT nombre,duracion_min,precio FROM servicios WHERE id=:id"), {"id": result["id"]}).mappings().one()
    assert row["nombre"] == datos["nombre"]
    assert row["duracion_min"] == 60
    assert str(row["precio"]) == "135.00"


@pytest.mark.caso("CP-09")
def test_cp09_disponibilidad_respeta_jornada(client, headers):
    s, fecha, _ = catalog(client, headers)
    data = call(client, headers, f"/disponibilidad?personal_id=3&servicio_id={s}&fecha={fecha}")["data"]
    slots = data["horarios"]
    assert slots
    assert any(h["hora_inicio"] == "09:00" and h["hora_fin"] == "10:00" for h in slots)
    assert all("09:00" <= h["hora_inicio"] < h["hora_fin"] <= "17:00" for h in slots)


@pytest.mark.caso("CP-10")
def test_cp10_reservar_cita(client, headers, motor):
    s, fecha, _ = catalog(client, headers)
    cita = call(client, headers, "/citas", "POST", {"personal_id": 3, "servicio_id": s, "fecha": fecha, "hora": "09:00"}, id=2, expected=201)["data"]
    with motor.connect() as c:
        row = c.execute(text("SELECT cliente_id,personal_id,estado,duracion_min FROM citas WHERE id=:id"), {"id": cita["id"]}).mappings().one()
    assert dict(row) == {"cliente_id": 2, "personal_id": 3, "estado": "pendiente", "duracion_min": 60}


@pytest.mark.caso("CP-11")
def test_cp11_rechazar_reserva_duplicada(client, headers, motor):
    s, fecha, _ = catalog(client, headers)
    datos = {"personal_id": 3, "servicio_id": s, "fecha": fecha, "hora": "09:00"}
    call(client, headers, "/citas", "POST", datos, id=2, expected=201)
    call(client, headers, "/citas", "POST", datos, id=4, expected=409)
    with motor.connect() as c:
        assert c.execute(text("SELECT COUNT(*) FROM citas")).scalar_one() == 1


@pytest.mark.caso("CP-13")
def test_cp13_reprogramar_cita(client, headers, motor):
    s, fecha, _ = catalog(client, headers)
    cita = call(client, headers, "/citas", "POST", {"personal_id": 3, "servicio_id": s, "fecha": fecha, "hora": "09:00"}, id=2, expected=201)["data"]["id"]
    call(client, headers, f"/citas/{cita}/reprogramar", "PATCH", {"fecha": fecha, "hora": "11:00"}, id=2)
    with motor.connect() as c:
        row = c.execute(text("SELECT TIME_FORMAT(hora,'%H:%i') AS hora,cliente_id,estado FROM citas WHERE id=:id"), {"id": cita}).mappings().one()
    assert dict(row) == {"hora": "11:00", "cliente_id": 2, "estado": "pendiente"}


@pytest.mark.caso("CP-15")
def test_cp15_cancelar_libera_intervalo(client, headers):
    s, fecha, _ = catalog(client, headers)
    cita = call(client, headers, "/citas", "POST", {"personal_id": 3, "servicio_id": s, "fecha": fecha, "hora": "09:00"}, id=2, expected=201)["data"]["id"]
    query = f"/disponibilidad?personal_id=3&servicio_id={s}&fecha={fecha}"
    assert not any(h["hora_inicio"] == "09:00" for h in call(client, headers, query)["data"]["horarios"])
    call(client, headers, f"/citas/{cita}/cancelar", "PATCH", id=2)
    assert any(h["hora_inicio"] == "09:00" for h in call(client, headers, query)["data"]["horarios"])


@pytest.mark.caso("CP-16")
def test_cp16_no_reprogramar_cita_ajena(client, headers, motor):
    s, fecha, _ = catalog(client, headers)
    cita = call(client, headers, "/citas", "POST", {"personal_id": 3, "servicio_id": s, "fecha": fecha, "hora": "09:00"}, id=2, expected=201)["data"]["id"]
    call(client, headers, f"/citas/{cita}/reprogramar", "PATCH", {"fecha": fecha, "hora": "11:00"}, id=4, expected=404)
    with motor.connect() as c:
        assert c.execute(text("SELECT TIME_FORMAT(hora,'%H:%i') FROM citas WHERE id=:id"), {"id": cita}).scalar_one() == "09:00"


@pytest.mark.caso("CP-17")
def test_cp17_logout_revoca_token(client):
    login = client.post("/api/v1/auth/login", json={"identificador": "cuenta2@example.com", "password": "PasswordTest2026!"})
    token = {"Authorization": "Bearer " + login.get_json()["data"]["access_token"]}
    assert client.get("/api/v1/auth/perfil", headers=token).status_code == 200
    assert client.post("/api/v1/auth/logout", headers=token).status_code == 200
    assert client.get("/api/v1/auth/perfil", headers=token).status_code == 401
