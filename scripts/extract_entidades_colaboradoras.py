from __future__ import annotations

import argparse
import csv
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber


DEFAULT_INPUT = Path("data/entidades/Entidades colaboradoras.pdf")
DEFAULT_OUTPUT = Path("data/entidades/entidades_colaboradoras.csv")
CSV_HEADERS = ["ENTIDAD", "PROVINCIA", "PÁGINA WEB "]
LINE_Y_TOLERANCE = 1.2


@dataclass(frozen=True)
class EntidadRow:
    entidad: str
    provincia: str
    pagina_web: str


@dataclass
class Line:
    y: float
    entity_parts: list[str] = field(default_factory=list)
    province_parts: list[str] = field(default_factory=list)
    url_parts: list[str] = field(default_factory=list)

    @property
    def entity_text(self) -> str:
        return join_text(self.entity_parts)

    @property
    def province_text(self) -> str:
        return join_text(self.province_parts)

    @property
    def url_text(self) -> str:
        return join_url(self.url_parts)


def normalize_key(text: str) -> str:
    return "".join(
        character
        for character in unicodedata.normalize("NFKD", text.upper())
        if character.isalnum()
    )


# All 50 Spanish provinces + 2 autonomous cities (Ceuta, Melilla).
# Canonical names match the most common form used in official documents.
ALL_PROVINCES = [
    # Andalucía
    "ALMERÍA", "CÁDIZ", "CÓRDOBA", "GRANADA",
    "HUELVA", "JAÉN", "MÁLAGA", "SEVILLA",
    # Aragón
    "HUESCA", "TERUEL", "ZARAGOZA",
    # Asturias
    "ASTURIAS",
    # Illes Balears
    "ILLES BALEARS",
    # Canarias
    "LAS PALMAS", "SANTA CRUZ DE TENERIFE",
    # Cantabria
    "CANTABRIA",
    # Castilla-La Mancha
    "ALBACETE", "CIUDAD REAL", "CUENCA", "GUADALAJARA", "TOLEDO",
    # Castilla y León
    "ÁVILA", "BURGOS", "LEÓN", "PALENCIA", "SALAMANCA",
    "SEGOVIA", "SORIA", "VALLADOLID", "ZAMORA",
    # Cataluña
    "BARCELONA", "GIRONA", "LLEIDA", "TARRAGONA",
    # Comunidad Valenciana
    "ALICANTE", "CASTELLÓN", "VALENCIA",
    # Extremadura
    "BADAJOZ", "CÁCERES",
    # Galicia
    "A CORUÑA", "LUGO", "ORENSE", "PONTEVEDRA",
    # La Rioja
    "LA RIOJA",
    # Madrid
    "MADRID",
    # Murcia
    "MURCIA",
    # Navarra
    "NAVARRA",
    # País Vasco
    "ÁLAVA", "BIZKAIA", "GIPUZKOA",
    # Ciudades autónomas
    "CEUTA", "MELILLA",
]

# Variant names used in co-official languages or alternative spellings.
# Maps normalized alias -> canonical province name from ALL_PROVINCES.
_PROVINCE_ALIASES: dict[str, str] = {
    # País Vasco — Basque variants
    "ARABA": "ÁLAVA",
    "ALABA": "ÁLAVA",
    "VIZCAYA": "BIZKAIA",
    "GUIPUZCOA": "GIPUZKOA",
    # Galicia — Galician / alternative Spanish
    "OURENSE": "ORENSE",
    "LA CORUÑA": "A CORUÑA",
    # Cataluña — Spanish variants
    "GERONA": "GIRONA",
    "LERIDA": "LLEIDA",
    # Illes Balears — Spanish variant
    "ISLAS BALEARES": "ILLES BALEARS",
    # Comunidad Valenciana — alternative names
    "CASTELLON DE LA PLANA": "CASTELLÓN",
    # Navarra — Basque variant
    "NAFARROA": "NAVARRA",
    # Typos in official document
    "CÓRODBA": "CÓRDOBA",
}


def build_province_lookup() -> dict[str, str]:
    province_by_key: dict[str, str] = {}
    for province in ALL_PROVINCES:
        key = normalize_key(province)
        province_by_key[key] = province
    for alias, canonical in _PROVINCE_ALIASES.items():
        province_by_key[normalize_key(alias)] = canonical
    return province_by_key


def join_text(parts: list[str]) -> str:
    value = ""
    for part in parts:
        token = " ".join(part.split())
        if not token:
            continue
        if token == "-":
            value = value.rstrip() + "-"
            continue
        if not value:
            value = token
            continue
        if value.endswith("-"):
            value += token
        elif token.startswith(("/", ")", ",", ".", ";", ":")):
            value += token
        else:
            value += f" {token}"
    return value.strip()


def join_url(parts: list[str]) -> str:
    return "".join(part.strip() for part in parts).strip()


def build_lines(page) -> list[Line]:
    lines: list[Line] = []
    words = page.extract_words(
        x_tolerance=2,
        y_tolerance=2,
        keep_blank_chars=False,
        use_text_flow=True,
    )

    for word in words:
        x = float(word["x0"])
        y = float(word["top"])
        text = word["text"]
        
        if y < 100:
            continue
            
        target_line = None
        for line in lines:
            if abs(line.y - y) <= LINE_Y_TOLERANCE:
                target_line = line
                break
        if target_line is None:
            target_line = Line(y=y)
            lines.append(target_line)

        if x < 280:
            target_line.entity_parts.append(text)
        elif x < 380:
            target_line.province_parts.append(text)
        else:
            target_line.url_parts.append(text)

    lines = [
        line
        for line in sorted(lines, key=lambda item: item.y)
        if line.entity_text or line.province_text or line.url_text
    ]

    for index, line in enumerate(lines):
        if line.province_text == "PROVINCIA":
            return lines[index:]

    return lines


def extract_province_records(
    lines: list[Line], page_number: int, province_by_key: dict[str, str]
) -> list[tuple[float, str]]:
    province_records: list[tuple[float, str]] = []
    province_parts: list[str] = []
    province_ys: list[float] = []

    for line in lines:
        if not line.province_text or line.province_text == "PROVINCIA":
            continue

        province_parts.append(line.province_text)
        province_ys.append(line.y)

        province_key = normalize_key(" ".join(province_parts))
        province = province_by_key.get(province_key)
        if province is not None:
            province_records.append((sum(province_ys) / len(province_ys), province))
            province_parts.clear()
            province_ys.clear()
            continue

        if any(candidate.startswith(province_key) for candidate in province_by_key):
            continue

        raise ValueError(
            f"Could not parse province on page {page_number}: {' '.join(province_parts)!r}"
        )

    if province_parts:
        raise ValueError(
            f"Incomplete province on page {page_number}: {' '.join(province_parts)!r}"
        )

    return province_records


def assign_lines_to_rows(
    lines: list[Line], province_records: list[tuple[float, str]]
) -> list[EntidadRow]:
    centers = [center for center, _province in province_records]
    rows = [
        {"entity_parts": [], "province": province, "url_parts": []}
        for _center, province in province_records
    ]

    boundaries: list[tuple[float, float]] = []
    for index, center in enumerate(centers):
        upper = (
            float("-inf") if index == 0 else (centers[index - 1] + center) / 2
        )
        lower = (
            float("inf")
            if index == len(centers) - 1
            else (center + centers[index + 1]) / 2
        )
        boundaries.append((upper, lower))

    for line in lines:
        if line.entity_text in {"ENTIDAD", "DE EXTRANJERÍA"}:
            continue
        if "ENTIDADES COLABORADORAS" in line.entity_text:
            continue

        for row, (upper, lower) in zip(rows, boundaries):
            if upper <= line.y < lower:
                if line.entity_text:
                    row["entity_parts"].append(line.entity_text)
                if line.url_text:
                    row["url_parts"].append(line.url_text)
                break

    return [
        EntidadRow(
            entidad=join_text(row["entity_parts"]),
            provincia=row["province"],
            pagina_web=join_url(row["url_parts"]),
        )
        for row in rows
    ]


def apply_known_fixes(rows: list[EntidadRow]) -> list[EntidadRow]:
    fixed_rows: list[EntidadRow] = []
    index = 0

    while index < len(rows):
        current = rows[index]
        following = rows[index + 1] if index + 1 < len(rows) else None
        after_following = rows[index + 2] if index + 2 < len(rows) else None

        if (
            following is not None
            and current.provincia == "LAS PALMAS"
            and current.entidad.endswith("Y")
            and following.entidad.startswith("DEPORTIVO ACCIONES UNIDAS ASOCIACIÓN ")
        ):
            prefix, suffix = following.entidad.split(" ASOCIACIÓN ", 1)
            fixed_rows.append(
                EntidadRow(
                    entidad=f"{current.entidad} {prefix}".strip(),
                    provincia=current.provincia,
                    pagina_web=current.pagina_web,
                )
            )
            fixed_rows.append(
                EntidadRow(
                    entidad=f"ASOCIACIÓN {suffix}".strip(),
                    provincia=following.provincia,
                    pagina_web=following.pagina_web,
                )
            )
            index += 2
            continue

        if (
            following is not None
            and after_following is not None
            and " FÉNIX ASOCIACIÓN " in current.entidad
            and following.provincia == "NAVARRA"
            and after_following.provincia == "NAVARRA"
            and after_following.entidad.startswith("MINORITARIOS EN NAVARRA FUNDACION KOINE")
        ):
            prefix, suffix = current.entidad.split(" FÉNIX ASOCIACIÓN ", 1)
            fenix_suffix, koine_suffix = after_following.entidad.split(
                " FUNDACION KOINE", 1
            )
            fixed_rows.append(
                EntidadRow(
                    entidad=prefix.strip(),
                    provincia=current.provincia,
                    pagina_web=current.pagina_web,
                )
            )
            fixed_rows.append(
                EntidadRow(
                    entidad=(
                        f"FÉNIX ASOCIACIÓN {suffix} {following.entidad} {fenix_suffix}"
                    ).strip(),
                    provincia=following.provincia,
                    pagina_web=following.pagina_web,
                )
            )
            fixed_rows.append(
                EntidadRow(
                    entidad=f"FUNDACION KOINE{koine_suffix}".strip(),
                    provincia=after_following.provincia,
                    pagina_web=after_following.pagina_web,
                )
            )
            index += 3
            continue

        if (
            following is not None
            and " FÉNIX ASOCIACIÓN " in current.entidad
            and following.provincia == "NAVARRA"
        ):
            prefix, suffix = current.entidad.split(" FÉNIX ASOCIACIÓN ", 1)
            fixed_rows.append(
                EntidadRow(
                    entidad=prefix.strip(),
                    provincia=current.provincia,
                    pagina_web=current.pagina_web,
                )
            )
            fixed_rows.append(
                EntidadRow(
                    entidad=f"FÉNIX ASOCIACIÓN {suffix} {following.entidad}".strip(),
                    provincia=following.provincia,
                    pagina_web=following.pagina_web,
                )
            )
            index += 2
            continue

        if (
            following is not None
            and current.provincia == "NAVARRA"
            and current.entidad.startswith("FÉNIX ASOCIACIÓN ")
            and following.entidad.startswith("MINORITARIOS EN NAVARRA FUNDACION KOINE")
        ):
            prefix, suffix = following.entidad.split(" FUNDACION KOINE", 1)
            fixed_rows.append(
                EntidadRow(
                    entidad=f"{current.entidad} {prefix}".strip(),
                    provincia=current.provincia,
                    pagina_web=current.pagina_web,
                )
            )
            fixed_rows.append(
                EntidadRow(
                    entidad=f"FUNDACION KOINE{suffix}".strip(),
                    provincia=following.provincia,
                    pagina_web=following.pagina_web,
                )
            )
            index += 2
            continue

        if (
            following is not None
            and " UNION DE PEQUEÑOS AGRICULTORES Y" in current.entidad
            and following.provincia == "TOLEDO"
        ):
            prefix, suffix = current.entidad.split(" UNION DE PEQUEÑOS AGRICULTORES Y", 1)
            fixed_rows.append(
                EntidadRow(
                    entidad=prefix.strip(),
                    provincia=current.provincia,
                    pagina_web=current.pagina_web,
                )
            )
            fixed_rows.append(
                EntidadRow(
                    entidad=(
                        f"UNION DE PEQUEÑOS AGRICULTORES Y{suffix} {following.entidad}"
                    ).strip(),
                    provincia=following.provincia,
                    pagina_web=following.pagina_web,
                )
            )
            index += 2
            continue

        fixed_rows.append(current)
        index += 1

    return fixed_rows


def extract_rows(pdf_path: Path) -> list[EntidadRow]:
    rows: list[EntidadRow] = []
    province_by_key = build_province_lookup()

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            lines = build_lines(page)
            province_records = extract_province_records(
                lines, page_number, province_by_key
            )
            rows.extend(assign_lines_to_rows(lines, province_records))

    return apply_known_fixes(rows)


def write_csv(rows: list[EntidadRow], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(CSV_HEADERS)
        for row in rows:
            writer.writerow([row.entidad, row.provincia, row.pagina_web])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract the entidades colaboradoras table from the PDF and write a CSV."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"PDF path to read. Defaults to {DEFAULT_INPUT}.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"CSV path to write. Defaults to {DEFAULT_OUTPUT}.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = extract_rows(args.input)
    write_csv(rows, args.output)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
