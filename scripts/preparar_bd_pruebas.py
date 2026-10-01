"""Prepara el esquema mínimo de CI únicamente en una base identificada de pruebas."""
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.sql_utils import cargar_sentencias


def main():
    raw = os.getenv("BELLEZA_TEST_DATABASE_URL")
    if not raw:
        raise SystemExit("Falta BELLEZA_TEST_DATABASE_URL; no se preparó ninguna base.")
    url = make_url(raw)
    if url.drivername != "mysql+pymysql" or not url.database or not url.database.endswith("_test"):
        raise SystemExit("Solo se acepta MySQL y una base aislada terminada en _test.")
    engine = create_engine(url, connect_args={"connect_timeout": 10})
    try:
        with engine.begin() as c:
            names = {row[0] for row in c.execute(text("SHOW TABLES"))}
            if names and "belleza_test_marker" not in names:
                raise SystemExit("La base contiene tablas sin marcador de pruebas; operación detenida.")
            c.exec_driver_sql("CREATE TABLE IF NOT EXISTS belleza_test_marker (id INT PRIMARY KEY)")
            c.exec_driver_sql("INSERT IGNORE INTO belleza_test_marker VALUES (1)")
            for path in [ROOT / "tests/sql/001_esquema_ci.sql", ROOT / "docker/mysql-init/00_auditoria.sql"]:
                for stmt in cargar_sentencias(path):
                    c.exec_driver_sql(stmt)
        print("Esquema mínimo preparado en la base aislada de pruebas.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
