"""Protecciones de la preparación de BD: rechazar destinos antes de escribir."""
from unittest.mock import MagicMock

import pytest
from scripts import preparar_bd_pruebas as preparar


@pytest.mark.parametrize("url", [
    "mysql+pymysql://usuario:clave@localhost/belleza_integral",
    "sqlite:///belleza_integral_test",
])
def test_rechaza_destino_invalido_sin_conectar(monkeypatch, url):
    monkeypatch.setenv("BELLEZA_TEST_DATABASE_URL", url)
    engine = MagicMock()
    monkeypatch.setattr(preparar, "create_engine", engine)
    with pytest.raises(SystemExit):
        preparar.main()
    engine.assert_not_called()


def test_exige_configuracion_de_pruebas(monkeypatch):
    monkeypatch.delenv("BELLEZA_TEST_DATABASE_URL", raising=False)
    with pytest.raises(SystemExit, match="Falta BELLEZA_TEST_DATABASE_URL"):
        preparar.main()


def test_rechaza_tablas_sin_marcador_antes_de_escribir(monkeypatch):
    monkeypatch.setenv("BELLEZA_TEST_DATABASE_URL", "mysql+pymysql://usuario:clave@localhost/aislada_test")
    engine = MagicMock()
    connection = engine.begin.return_value.__enter__.return_value
    connection.execute.return_value = [("usuarios",)]
    monkeypatch.setattr(preparar, "create_engine", lambda *a, **k: engine)
    with pytest.raises(SystemExit, match="sin marcador"):
        preparar.main()
    connection.exec_driver_sql.assert_not_called()
    engine.dispose.assert_called_once()
