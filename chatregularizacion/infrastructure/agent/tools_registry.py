from typing import Literal
from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field

from domain.ports.entidad_colaboradora_repository_port import EntidadColaboradoraRepositoryPort

class SearchEntidadColaboradoraInput(BaseModel):
    provincia: Literal[
        'A CORUÑA', 'ALBACETE', 'ALMERÍA', 'ASTURIAS', 'BADAJOZ', 'BARCELONA', 'BIZKAIA', 
        'CASTELLÓN /CASTELLÓ', 'CÁDIZ', 'CÓRDOBA', 'GIRONA', 'GRANADA', 'GUIPUZKOA', 
        'HUELVA', 'JAÉN', 'LAS PALMAS', 'LLEIDA', 'LUGO', 'MADRID', 'MELILLA', 'MURCIA', 
        'MÁLAGA', 'NAVARRA', 'ORENSE / OURENSE', 'PALENCIA', 'PONTEVEDRA', 'SALAMANCA', 
        'SANTA CRUZ DE TENERIFE', 'SEVILLA', 'TARRAGONA', 'TOLEDO', 'VALENCIA / VALÈNCIA', 
        'VALLADOLID', 'ZARAGOZA', 'ÁLABA / ARABA', 'ÁLAVA / ARABA'
    ] = Field(
        description="Nombre de la provincia donde buscar entidades colaboradoras."
    )

def build_tools(
        entidad_colaboradora_repository: EntidadColaboradoraRepositoryPort
)-> list[BaseTool]:

    @tool("search_entidades_colaboradoras", args_schema=SearchEntidadColaboradoraInput)
    def search_entidades_colaboradoras(provincia: str) -> str:
        """
        Busca entidades colaboradoras en una provincia específica.
        
        Usa siempre esta herramienta cuando el usuario pregunte por asociaciones, organizaciones 
        o entidades que puedan ayudar en su proceso de regularización en una provincia de España.
        Devuelve una lista de entidades y sus páginas web si están disponibles.
        """
        entities = entidad_colaboradora_repository.get_by_provincia(provincia)
        if not entities:
            return f"No se encontraron entidades colaboradoras en {provincia}."
        
        result = [f"Entidades colaboradoras en {provincia}:"]
        for entity in entities:
            web_info = f" - Web: {entity.web_page}" if entity.web_page else ""
            result.append(f"- {entity.nombre}{web_info}")
        
        return "\n".join(result)
    
    return [search_entidades_colaboradoras]