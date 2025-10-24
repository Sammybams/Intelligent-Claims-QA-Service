import os

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeOutputOption, AnalyzeResult
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

KEY = os.getenv("DOCUMENTINTELLIGENCE_API_KEY")
ENDPOINT = os.getenv("DOCUMENTINTELLIGENCE_ENDPOINT")

def make_pdf_searchable(doc: bytes, document_id: str):
    """
    Converts a document to a searchable PDF using Azure Document Intelligence.

    Args:

        doc (bytes): The document content in bytes.
        document_id (str): The identifier for the document.

    Returns:
        str: The filename of the generated searchable PDF.
    """
    
    document_intelligence_client = DocumentIntelligenceClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))


    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-read",
        AnalyzeDocumentRequest(bytes_source=doc),
        output = [AnalyzeOutputOption.PDF]
    )

    result: AnalyzeResult = poller.result()
    operation_id = poller.details["operation_id"]


    response = document_intelligence_client.get_analyze_result_pdf(model_id=result.model_id, result_id=operation_id)
    with open(f"{document_id}.pdf", "wb") as writer:
        writer.writelines(response)

    return f"{document_id}.pdf"