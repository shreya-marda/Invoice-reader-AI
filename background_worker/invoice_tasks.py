from celery import Celery
from azure.storage.blob import BlobServiceClient
import zipfile
import io
import requests
from bson import ObjectId
from config.config import collection
from config.blob import AZURE_CONNECTION_STRING, AZURE_CONTAINER_NAME
from Invoice_processing.invoice_reader import analyze_invoice

celery_app = Celery("invoice_tasks", broker="redis://redis:6379/0")
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
def convert_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    else:
        return obj

def upload_bytes_to_blob(file_bytes, blob_name):
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file_bytes, overwrite=True)
    return blob_client.url

@celery_app.task
def process_invoice_files(process_id, filename, file_bytes, app_key, is_zip,
                          promo_event_name=None, start_date=None, end_date=None, locale=None):
    response_data = {}
    try:
        if is_zip:
            zip_folder = filename.rsplit(".", 1)[0]
            with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as zip_ref:
                extracted_files = [f for f in zip_ref.namelist() if not f.startswith("__MACOSX") and not f.endswith("/")]
                for extracted_file in extracted_files:
                    extracted_bytes = zip_ref.read(extracted_file)
                    blob_name = f"{promo_event_name}/{zip_folder}/{extracted_file}"
                    blob_url = upload_bytes_to_blob(extracted_bytes, blob_name)
                    try:
                        data = analyze_invoice(blob_url)
                        # data = {}
                        data["_id"] = str(ObjectId())
                        data["process_id"] = process_id
                        data["filename"] = extracted_file
                        data["blob_url"] = blob_url
                        data["app_key"] = app_key
                        data["status"] = "processing"
                        data["promo_event_name"] = promo_event_name
                        data["start_date"] = start_date
                        data["end_date"] = end_date
                        data["locale"] = locale
                        cleaned_data = convert_objectid(data)
                        collection.insert_one(cleaned_data)
                        response_data[extracted_file] = cleaned_data
                    except Exception as e:
                        response_data[extracted_file] = {"error": str(e)}
        else:
            blob_name = f"{promo_event_name}/invoices/{filename}"
            blob_url = upload_bytes_to_blob(file_bytes, blob_name)
            try:
                data = analyze_invoice(blob_url)
                # data = {}
                data["_id"] = str(ObjectId())
                data["process_id"] = process_id
                data["filename"] = filename
                data["blob_url"] = blob_url
                data["app_key"] = app_key
                data["status"] = "processing"
                data["promo_event_name"] = promo_event_name
                data["start_date"] = start_date
                data["end_date"] = end_date
                data["locale"] = locale
                cleaned_data = convert_objectid(data)
                collection.insert_one(cleaned_data)
                response_data[extracted_file] = cleaned_data
            except Exception as e:
                response_data[filename] = {"error": str(e)}

        collection.update_many(
            {"process_id": process_id},
            {"$set": {"status": "completed"}}
        )

    except Exception as main_e:
        collection.update_many(
            {"process_id": process_id},
            {"$set": {"status": "failed", "error": str(main_e)}}
        )
