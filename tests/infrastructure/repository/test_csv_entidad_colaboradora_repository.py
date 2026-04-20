import pytest
from pathlib import Path

from domain.entidad_colaboradora import EntidadColaboradora
from infrastructure.repository.csv_entidad_colaboradora_repository import CsvEntidadColaboradoraRepositoryAdapter

@pytest.fixture
def mock_csv_file(tmp_path: Path):
    csv_content = """ENTIDAD;PROVINCIA;PÁGINA WEB \nASOCIACIÓN ALMERÍA ACOGE;ALMERÍA;https://www.almeriaacoge.org/\nASOCIACIÓN DE MUJERES LATRÉBEDE;ALMERÍA;  \nASOCIACIÓN CATNOVA;BARCELONA;https://www.catnova.cat/\n"""
    file_path = tmp_path / "mock_entidades.csv"
    file_path.write_text(csv_content, encoding='utf-8-sig')
    return file_path

def test_get_by_provincia_exact_match(mock_csv_file):
    adapter = CsvEntidadColaboradoraRepositoryAdapter(file_path=mock_csv_file)
    results = adapter.get_by_provincia("ALMERÍA")
    
    assert len(results) == 2
    assert results[0].nombre == "ASOCIACIÓN ALMERÍA ACOGE"
    assert results[0].provincia == "ALMERÍA"
    assert results[0].web_page == "https://www.almeriaacoge.org/"

    assert results[1].nombre == "ASOCIACIÓN DE MUJERES LATRÉBEDE"
    assert results[1].web_page is None

def test_get_by_provincia_case_insensitive(mock_csv_file):
    adapter = CsvEntidadColaboradoraRepositoryAdapter(file_path=mock_csv_file)
    results = adapter.get_by_provincia("barcelona")
    
    assert len(results) == 1
    assert results[0].nombre == "ASOCIACIÓN CATNOVA"

def test_get_by_provincia_no_match(mock_csv_file):
    adapter = CsvEntidadColaboradoraRepositoryAdapter(file_path=mock_csv_file)
    results = adapter.get_by_provincia("MADRID")
    
    assert len(results) == 0
