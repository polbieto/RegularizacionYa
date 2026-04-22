import pytest
from pathlib import Path

from domain.entidad_colaboradora import EntidadColaboradora
from infrastructure.repository.csv_entidad_colaboradora_repository import CsvEntidadColaboradoraRepositoryAdapter

@pytest.fixture
def real_csv_file():
    return Path("data/entidades/entidades_colaboradoras.csv")

def test_get_by_provincia_exact_match(real_csv_file):
    adapter = CsvEntidadColaboradoraRepositoryAdapter(file_path=real_csv_file)
    results = adapter.get_by_provincia("ALMERÍA")
    
    assert len(results) > 0
    assert all("ALMER" in r.provincia.upper() for r in results)

def test_get_by_provincia_case_insensitive(real_csv_file):
    adapter = CsvEntidadColaboradoraRepositoryAdapter(file_path=real_csv_file)
    results = adapter.get_by_provincia("barcelona")
    
    assert len(results) > 0
    assert all("BARCELONA" in r.provincia.upper() for r in results)

def test_get_by_provincia_no_match(real_csv_file):
    adapter = CsvEntidadColaboradoraRepositoryAdapter(file_path=real_csv_file)
    results = adapter.get_by_provincia("NARNIA")
    
    assert len(results) == 0

@pytest.mark.parametrize("provincia_search, expected_count", [
    ("ÁLAVA", 5),
    ("ARABA", 5),
    ("alava", 5),
    ("araba", 5)
])
def test_get_by_provincia_alava_araba(real_csv_file, provincia_search, expected_count):
    adapter = CsvEntidadColaboradoraRepositoryAdapter(file_path=real_csv_file)
    results = adapter.get_by_provincia(provincia_search)
    assert len(results) == expected_count
