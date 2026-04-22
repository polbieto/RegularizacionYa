import csv
import logging
from pathlib import Path
from typing import Sequence

from domain.entidad_colaboradora import EntidadColaboradora
from domain.ports.entidad_colaboradora_repository_port import EntidadColaboradoraRepositoryPort

import pandas as pd

logger = logging.getLogger(__name__)
class CsvEntidadColaboradoraRepositoryAdapter(EntidadColaboradoraRepositoryPort):
    
    def __init__(self, file_path: Path = Path("data/entidades/entidades_colaboradoras.csv")):
        self.file_path = file_path

    def get_by_provincia(self, provincia: str) -> Sequence[EntidadColaboradora]:
        df = pd.read_csv(self.file_path, sep=';', encoding='utf-8-sig', keep_default_na=False)
        
        import unicodedata
        def remove_accents(s: str) -> str:
            return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
        
        provincia_upper = remove_accents(provincia.upper().strip())
        
        s_provincia = df['PROVINCIA'].apply(lambda x: remove_accents(str(x).upper()))
        
        if provincia_upper in ('ALAVA', 'ARABA', 'ALABA'):
            filtered = df[s_provincia.str.contains('ALAVA|ALABA|ARABA', na=False, regex=True)]
        else:
            filtered = df[s_provincia.str.contains(provincia_upper, na=False, regex=False)]
        
        results = [
            EntidadColaboradora(
                nombre=row.get('ENTIDAD', '').strip(),
                provincia=row.get('PROVINCIA', '').strip(),
                web_page=row.get('PÁGINA WEB ', '').strip() or None
            )
            for _, row in filtered.iterrows()
        ]
        logger.info("Datos de la entidades %s", results)
        return results
