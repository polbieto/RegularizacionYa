from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "extract_entidades_colaboradoras.py"


def load_script_module():
    spec = importlib.util.spec_from_file_location(
        "extract_entidades_colaboradoras", SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_extract_rows_handles_multi_line_entities():
    module = load_script_module()
    rows = module.extract_rows(ROOT / "data" / "entidades" / "Entidades colaboradoras.pdf")

    assert len(rows) == 215

    lookup = {(row.entidad, row.provincia): row.pagina_web for row in rows}

    assert (
        lookup[
            (
                "ASOCIACIÓN SOCIAL, SANITARIA, CULTURAL, EDUCATIVO, CIENTIFICO Y "
                "DEPORTIVO ACCIONES UNIDAS",
                "LAS PALMAS",
            )
        ]
        == "https://www.asociacionaccionesunidas.com/"
    )
    assert (
        lookup[
            (
                "FÉNIX ASOCIACIÓN DE APOYO AL REFUGIADO E INMIGRANTES LGBTI+ Y "
                "COLECTIVOS MINORITARIOS EN NAVARRA",
                "NAVARRA",
            )
        ]
        == "https://fenixasociacion.org/"
    )
    assert (
        lookup[
            (
                "UNION DE PEQUEÑOS AGRICULTORES Y GANADEROS DE CASTILLA-LA MANCHA "
                "(UPA CLM)",
                "TOLEDO",
            )
        ]
        == ""
    )


def test_write_csv_uses_expected_headers_and_delimiter(tmp_path: Path):
    module = load_script_module()
    rows = [
        module.EntidadRow(
            entidad="ASOCIACIÓN ARRAIANAS",
            provincia="A CORUÑA",
            pagina_web="https://www.arraianas.org/es",
        )
    ]
    output_path = tmp_path / "entidades_colaboradoras.csv"

    module.write_csv(rows, output_path)

    with output_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.reader(csv_file, delimiter=";")
        written_rows = list(reader)

    assert written_rows == [
        ["ENTIDAD", "PROVINCIA", "PÁGINA WEB "],
        ["ASOCIACIÓN ARRAIANAS", "A CORUÑA", "https://www.arraianas.org/es"],
    ]
