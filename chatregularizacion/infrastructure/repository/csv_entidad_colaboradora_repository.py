import csv
from pathlib import Path
from typing import Sequence

from domain.entidad_colaboradora import EntidadColaboradora
from domain.ports.entidad_colaboradora_repository_port import EntidadColaboradoraRepositoryPort

class CsvEntidadColaboradoraRepositoryAdapter(EntidadColaboradoraRepositoryPort):
    
    def __init__(self, file_path: Path = Path("data/entidades_colaboradoras.csv")):
        self.file_path = file_path

    def get_by_provincia(self, provincia: str) -> Sequence[EntidadColaboradora]:
        provincia_upper = provincia.upper().strip()
        results = []
        with open(self.file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                # Use standard dictionary keys found in the CSV
                # Note: open(..., encoding='utf-8-sig') strips \ufeff so 'ENTIDAD' works
                row_provincia = row.get('PROVINCIA', '').strip().upper()
                if provincia_upper in row_provincia:
                    web_page = row.get('PÁGINA WEB ', '').strip()
                    results.append(
                        EntidadColaboradora(
                            nombre=row.get('ENTIDAD', '').strip(),
                            provincia=row.get('PROVINCIA', '').strip(),
                            web_page=web_page if web_page else None
                        )
                    )
        return results
