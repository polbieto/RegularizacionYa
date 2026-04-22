from typing import Literal
from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field

from domain.ports.entidad_colaboradora_repository_port import EntidadColaboradoraRepositoryPort

class SearchEntidadColaboradoraInput(BaseModel):
    provincias: list[str] = Field(
        description="Lista de nombres de las provincias donde buscar entidades. Extrae todas las provincias de la petición del usuario y mapea sus nombres (incluso si tienen errores tipográficos) a las provincias oficiales válidas: A CORUÑA, ALBACETE, ALMERÍA, ARABA, ASTURIAS, BADAJOZ, BARCELONA, BIZKAIA, CASTELLÓ, CÁDIZ, CÓRDOBA, GIRONA, GRANADA, GUIPUZKOA, HUELVA, JAÉN, LAS PALMAS, LLEIDA, LUGO, MADRID, MELILLA, MURCIA, MÁLAGA, NAVARRA, OURENSE, PALENCIA, PONTEVEDRA, SALAMANCA, SANTA CRUZ DE TENERIFE, SEVILLA, TARRAGONA, TOLEDO, VALENCIA, VALLADOLID, ZARAGOZA. Si el usuario pide varias, inclúyelas todas en la lista."
    )

def build_tools(
        entidad_colaboradora_repository: EntidadColaboradoraRepositoryPort
)-> list[BaseTool]:

    @tool("search_entidades_colaboradoras", args_schema=SearchEntidadColaboradoraInput)
    def search_entidades_colaboradoras(provincias: list[str]) -> str:
        """
        Busca entidades colaboradoras en una o varias provincias específicas.
        
        Usa siempre esta herramienta cuando el usuario pregunte por asociaciones, organizaciones 
        o entidades que puedan ayudar en su proceso de regularización en España.
        Devuelve una lista de entidades y sus páginas web si están disponibles.
        IMPORTANTE: Si la herramienta indica que no hay entidades, NO inventes entidades.
        """
        if not provincias:
            return "No se especificó ninguna provincia válida."

        all_results = []
        for provincia in provincias:
            entities = entidad_colaboradora_repository.get_by_provincia(provincia)
            if not entities:
                all_results.append(f"No se encontraron entidades colaboradoras en {provincia}. IMPORTANTE: No inventes entidades para esta provincia, indica al usuario que no hay entidades registradas en nuestra base de datos para {provincia}.")
                continue
            
            result = [f"Entidades colaboradoras en {provincia}:"]
            for entity in entities:
                web_info = f" - Web: {entity.web_page}" if entity.web_page else ""
                result.append(f"- {entity.nombre}{web_info}")
            all_results.append("\n".join(result))
        
        return "\n\n".join(all_results)
    
    return [search_entidades_colaboradoras]