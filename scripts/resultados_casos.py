"""Copia las fichas de diseño y añade solo resultados comprobados en JUnit."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = json.loads((ROOT / "docs/casos_prueba_devops2.json").read_text(encoding="utf-8"))
    report = json.loads((ROOT / "artifacts/resultados.json").read_text(encoding="utf-8"))
    source["ejecucion"] = report["entorno"]
    for caso in source["casos"]:
        tests = report["casos"].get(caso["id"], [])
        if not tests:
            caso["resultado_obtenido"] = "No ejecutado. Requiere revisión manual de UX." if caso["id"] == "CP-21" else "No ejecutado. Requiere validación y decisión del representante del negocio."
            continue
        states = {t["estado"] for t in tests}
        caso["estado"] = "Fallido" if "Fallido" in states else "No ejecutado" if "No ejecutado" in states else "Aprobado"
        caso["resultado_obtenido"] = (f"{len(tests)} comprobación(es) automatizada(s) con estado {caso['estado'].lower()}. "
                                      + ("Se verificaron las condiciones esperadas de los pasos." if caso["estado"] == "Aprobado" else "Consultar el detalle del reporte HTML y JUnit."))
        caso["evidencia"] = "unitarias.html y unitarias.xml" if caso["nivel"] == "Unitaria" else "selenium.html, selenium.xml y captura" if caso["nivel"] == "Sistema" else "integracion.html e integracion.xml"
        caso["pruebas_ejecutadas"] = tests
    destination = ROOT / "artifacts/casos-ejecutados.json"
    destination.write_text(json.dumps(source, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Resultados por caso guardados sin modificar las fichas de diseño.")


if __name__ == "__main__":
    main()
