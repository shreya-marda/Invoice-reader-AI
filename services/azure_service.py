from src.blob import AZURE_CONNECTION_STRING, AZURE_CONTAINER_NAME, endpoint, key
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
# from src.config import endpoint, key

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

def upload_bytes_to_blob(file_bytes, blob_name):
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file_bytes, overwrite=True)
    return blob_client.url


def poller_azure(blob_url):
    poller = document_analysis_client.begin_analyze_document_from_url(
        "prebuilt-invoice", document_url=blob_url, locale="en-US"
    )
    return poller
