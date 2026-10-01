"""Ejecuta suites separadas y conserva HTML, JUnit y resultados por caso."""
import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITES = {
    "unitarias": ["tests/unit"],
    "integracion": ["tests", "--ignore=tests/unit", "--ignore=tests/e2e"],
    "selenium": ["tests/e2e"],
}


def contexto():
    packages = {}
    for name in ["Flask", "SQLAlchemy", "PyMySQL", "pytest", "pytest-html", "selenium"]:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "No instalado"
    def git(*args):
        p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
        return p.stdout.strip() if p.returncode == 0 else "No disponible"
    memoria = "No disponible"
    if Path("/proc/meminfo").exists():
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemTotal:"):
                memoria = line.split(":", 1)[1].strip()
    distribucion = "No disponible"
    if hasattr(platform, "freedesktop_os_release"):
        try:
            distribucion = platform.freedesktop_os_release().get("PRETTY_NAME", distribucion)
        except OSError:
            pass
    return {"fecha_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
            "distribucion": distribucion,
            "sistema": platform.platform(), "arquitectura": platform.machine(),
            "cpu_logicas_visibles": os.cpu_count(), "memoria_visible": memoria,
            "nota_hardware": "Recursos visibles al proceso; no indican una asignación exclusiva.",
            "git_sha": git("rev-parse", "HEAD"), "rama": git("branch", "--show-current"),
            "cambios_sin_commit": bool(git("status", "--porcelain")), "paquetes": packages,
            "zona_negocio": "America/Guatemala", "tipo_ambiente": "Pruebas aisladas locales o CI"}


def leer_junit(path):
    tests = []
    for node in ET.parse(path).getroot().iter("testcase"):
        estado = "Aprobado"
        if node.find("failure") is not None or node.find("error") is not None:
            estado = "Fallido"
        elif node.find("skipped") is not None:
            estado = "No ejecutado"
        props = {p.attrib.get("name"): p.attrib.get("value") for p in node.findall("properties/property")}
        tests.append({"nombre": node.attrib.get("name"), "clase": node.attrib.get("classname"),
                      "segundos": float(node.attrib.get("time", 0)), "caso": props.get("caso"),
                      "navegador": props.get("navegador"), "estado": estado})
    return tests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=["todas", *SUITES], default="todas")
    args = parser.parse_args()
    chosen = list(SUITES) if args.suite == "todas" else [args.suite]
    if any(s != "unitarias" for s in chosen) and not os.getenv("BELLEZA_TEST_DATABASE_URL"):
        raise SystemExit("Falta la base aislada: no se aceptan pruebas omitidas como aprobadas.")
    directory = ROOT / "artifacts"
    directory.mkdir(exist_ok=True)
    info = contexto()
    if os.getenv("BELLEZA_TEST_DATABASE_URL"):
        from sqlalchemy import create_engine, text
        from sqlalchemy.engine import make_url
        url = make_url(os.environ["BELLEZA_TEST_DATABASE_URL"])
        if not url.database or not url.database.endswith("_test"):
            raise SystemExit("La base de pruebas debe terminar en _test.")
        engine = create_engine(url)
        try:
            with engine.connect() as c:
                info["mysql"] = c.execute(text("SELECT VERSION()")).scalar_one()
        finally:
            engine.dispose()
    (directory / "entorno.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    failed = False
    resumen = {"entorno": info, "suites": [], "casos": {}}
    for suite in chosen:
        xml = directory / f"{suite}.xml"
        # Evitar asociar resultados antiguos con una nueva ejecución fallida.
        xml.unlink(missing_ok=True)
        html = directory / f"{suite}.html"
        html.unlink(missing_ok=True)
        command = [sys.executable, "-m", "pytest", *SUITES[suite], "-v", "--tb=short",
                   f"--html={html}", "--self-contained-html", f"--junitxml={xml}"]
        result = subprocess.run(command, cwd=ROOT)
        tests = leer_junit(xml) if xml.exists() else []
        incomplete = not tests or any(t["estado"] == "No ejecutado" for t in tests)
        failed = failed or result.returncode != 0 or incomplete
        resumen["suites"].append({"nombre": suite, "exit_code": result.returncode, "pruebas": tests,
                                "completa": not incomplete})
        for test in tests:
            if test["caso"]:
                resumen["casos"].setdefault(test["caso"], []).append(test)
    resumen["resultado_global"] = "Fallido o incompleto" if failed else "Aprobado"
    filename = directory / ("resultados.json" if args.suite == "todas" else f"resultados-{args.suite}.json")
    filename.write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
