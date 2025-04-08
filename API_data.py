# from fastapi import FastAPI, File, UploadFile, Query
# import os
# import zipfile
# from azure.storage.blob import BlobServiceClient
# from config import collection
# from blob import AZURE_CONNECTION_STRING, AZURE_CONTAINER_NAME
# import logging
# from bson import ObjectId
# from invoice_reader import analyze_invoice
# import io

# # Logging setup
# logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# logger = logging.getLogger(__name__)

# # FastAPI App
# app = FastAPI()

# # Azure Blob Storage setup
# blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
# container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)


# # Convert ObjectId to string for JSON responses
# def convert_objectid(obj):
#     if isinstance(obj, ObjectId):
#         return str(obj)
#     elif isinstance(obj, dict):
#         return {k: convert_objectid(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [convert_objectid(item) for item in obj]
#     else:
#         return obj

# # # Sanitize filename
# # def sanitize_filename(filename):
# #     return filename.replace("/", "_").replace("\\", "_")

# # Upload file to Azure Blob Storage
# async def upload_to_blob(file: UploadFile, blob_folder: str):
#     blob_name = f"{blob_folder}/{file.filename}"
#     blob_client = container_client.get_blob_client(blob_name)

#     # Upload file directly from memory
#     blob_client.upload_blob(file.file, overwrite=True)
#     return blob_client.url


# # API Endpoint to Upload and Process Invoices
# @app.post("/invoice-reader")
# async def invoice_reader(file: UploadFile = File(...), app_key: str = Query(..., description="Application key for authentication")):
#     response_data = {}
  

#     if file.filename.endswith(".zip"):
#         try:
#             # Read ZIP file in memory
#             zip_bytes = await file.read()
#             zip_folder = file.filename.rsplit(".", 1)[0]

#             with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_ref:
#                 extracted_files = [f for f in zip_ref.namelist() if not f.startswith("__MACOSX") and not f.endswith("/")]

#                 for extracted_file in extracted_files:
#                     extracted_bytes = zip_ref.read(extracted_file)
#                     extracted_upload_file = UploadFile(filename=extracted_file, file=io.BytesIO(extracted_bytes))

#                     blob_url = await upload_to_blob(extracted_upload_file, zip_folder)
#                     try:
#                         # data = {}
#                         data = analyze_invoice(blob_url)
#                         data["_id"] = str(ObjectId())
#                         data["filename"] = extracted_file
#                         data["blob_url"] = blob_url
#                         data["app_key"] = app_key

#                         cleaned_data = convert_objectid(data)
#                         collection.insert_one(cleaned_data)
#                         response_data[extracted_file] = cleaned_data
#                     except Exception as e:
#                         response_data[extracted_file] = {"error": str(e)}

#             return {"status": "success", "zip_folder": zip_folder, "processed_files": response_data}

#         except Exception as e:
#             return {"error": str(e)}

#     else:
#         blob_url = await upload_to_blob(file, "invoices")
#         try:
#             data = analyze_invoice(blob_url)
#             # data = {}
#             data["_id"] = str(ObjectId())
#             data["filename"] = file.filename
#             data["blob_url"] = blob_url
#             data["app_key"] = app_key

#             cleaned_data = convert_objectid(data)
#             collection.insert_one(cleaned_data)
#             return {"status": "success", "processed_file": cleaned_data}
#         except Exception as e:
#             return {"error": str(e)}
        

# @app.get("/status")
# async def status(process_id: str):
    
#     return {"status": "success", "zip_folder": "abcd.zip" , "processed_files": "blob path"}









# from fastapi import FastAPI, File, UploadFile, Query
# import os
# from bson import ObjectId
# from config import collection
# from blob import AZURE_CONNECTION_STRING, AZURE_CONTAINER_NAME
# from azure.storage.blob import BlobServiceClient
# import io
# import logging
# from invoice_tasks import process_invoice_files

# logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# logger = logging.getLogger(__name__)

# app = FastAPI()

# blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
# container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

# def convert_objectid(obj):
#     if isinstance(obj, ObjectId):
#         return str(obj)
#     elif isinstance(obj, dict):
#         return {k: convert_objectid(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [convert_objectid(item) for item in obj]
#     else:
#         return obj

# @app.post("/invoice-reader")
# async def invoice_reader(
#     file: UploadFile = File(...),
#     app_key: str = Query(...),
#     # webhook_url: str = Query(None)
# ):
#     process_id = str(ObjectId())
#     file_bytes = await file.read()
#     is_zip = file.filename.endswith(".zip")

#     process_invoice_files.delay(
#         process_id,
#         file.filename,
#         file_bytes,
#         app_key,
#         is_zip,
#         # webhook_url
#     )

#     return {"process_id": process_id}

# @app.get("/invoice-status/{process_id}")
# def get_status(process_id: str):
#     records = list(collection.find({"process_id": process_id}))
    
#     if not records:
#         return {
#             "status": "processing",
#             "process_id": process_id,
#             "records": []
#         }

#     # If records exist, try getting the status from the first one
#     status = records[0].get("status", "processing")

#     return {
#         "status": status,
#         "process_id": process_id,
#         "records": convert_objectid(records)
#     }


from fastapi import FastAPI, File, UploadFile, Query
import os
from bson import ObjectId
from config.config import collection
from config.blob import AZURE_CONNECTION_STRING, AZURE_CONTAINER_NAME
from azure.storage.blob import BlobServiceClient
import io
import logging
from background_worker.invoice_tasks import process_invoice_files

logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

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

def convert_objectid_for_status(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k == "_id":
                new_obj["invoice_id"] = str(v)
            else:
                new_obj[k] = convert_objectid_for_status(v)
        return new_obj
    elif isinstance(obj, list):
        return [convert_objectid_for_status(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj
    
@app.post("/invoice-reader")
async def invoice_reader(
    file: UploadFile = File(...),
    app_key: str = Query(...),
    promo_event_name: str = Query(...),
    start_date: str = Query(..., description="Format: DD-MM-YYYY"),
    end_date: str = Query(..., description="Format: DD-MM-YYYY"),
    locale: str = Query(...)
):
    process_id = str(ObjectId())
    file_bytes = await file.read()
    is_zip = file.filename.endswith(".zip")

    process_invoice_files.delay(
        process_id,
        file.filename,
        file_bytes,
        app_key,
        is_zip,
        promo_event_name,
        start_date,
        end_date,
        locale
    )

    return {"process_id": process_id}

@app.get("/invoice-status/{process_id}")
def get_status(process_id: str):
    records = list(collection.find({"process_id": process_id}))
    if not records:
        return {
            "status": "processing",
            "process_id": process_id,
            "records": []
        }
    status = records[0].get("status", "processing")
    task_data = [
            {
                "invoice_id": str(record["_id"]),
                "process_id": record["process_id"]
            }
            for record in records
        ]

    return {
            "status": status,
            "process_id": process_id,
            "records": task_data
        }

@app.get("/invoice-data/")
def get_invoice_data(process_id: str = Query(...), invoice_id: str = Query(None)):
    if invoice_id:
        record = collection.find_one({"process_id": process_id, "_id": invoice_id})
        if not record:
            return {"error": "No data found for the given process_id and invoice_id"}
        return convert_objectid(record)
    else:
        records = list(collection.find({"process_id": process_id}))
        if not records:
            return {"error": "No data found for the given process_id"}
        return convert_objectid_for_status(records)
