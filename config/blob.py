from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv

load_dotenv()


# Azure credentials 
endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

# Use the copied connection string here
AZURE_CONNECTION_STRING =os.getenv("AZURE_CONNECTION_STRING")
AZURE_CONTAINER_NAME =os.getenv("CONTAINER_NAME")

# # Initialize the BlobServiceClient
# blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

# # Example of interacting with Blob Storage
# container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
