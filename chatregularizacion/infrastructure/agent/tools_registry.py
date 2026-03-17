from chatregularizacion.application.services.document_service import DocumentService
from langchain_core.tools import BaseTool
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class SearchOnDocumentsInput(BaseModel):
    query: str = Field(
        description="Specific question to search in the base knowledge.",
    )

def build_tools(
        document_service: DocumentService
)-> list[BaseTool]:

    @tool("search_on_documents", args_schema=SearchOnDocumentsInput)
    def search_on_documents(query: str) -> str:
        """
        Base knowledge to answer any question.
        
        This knowledge base contains the context, requirements, deadlines, 
        documentation needed, situations for access (like labor, family, vulnerability), 
        asylum seeker information, procedures to prove stay in Spain without a 'padrón' ,
        how to present the application, and general
        warnings about scams, among other topics.

        Always use this tool to answer questions.

        """
        return document_service.search_documents(query=query)
    
    return [search_on_documents]