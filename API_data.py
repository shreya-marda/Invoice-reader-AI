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


from fastapi import FastAPI, File, UploadFile, Query, Header, HTTPException
import os
from bson import ObjectId
from config.config import collection_invoices_data, collection_products
from config.blob import AZURE_CONNECTION_STRING, AZURE_CONTAINER_NAME
from azure.storage.blob import BlobServiceClient
import io
import logging
from background_worker.invoice_tasks import process_invoice_files
# from dotenv import load_dotenv
import pymongo
import pandas as pd
import numpy as np
from fastapi.responses import JSONResponse
from product_matching.data_preprocessing import preprocess, get_embedding
from product_matching.search import search_product_by_vector
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from typing import Optional
from src.utils import convert_objectid, convert_objectid_for_status, ObjectId



logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# logger = logging.getLogger(__name__)

# load_dotenv()

# MONGO_URI = os.getenv("MONGODB_URI")

# MongoDB Connection
# client = pymongo.MongoClient(MONGO_URI)
# db = client.promo
# collection_products = db.products
# collection_invoices_data = db.invoices

    
@app.post("/invoice-reader")
async def invoice_reader(
    file: UploadFile = File(...),
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
    logger.info(f"records: {records}")
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

# @app.get("/invoice-data/")
# def get_invoice_data(process_id: str = Query(...), invoice_id: str = Query(None)):
#     if invoice_id:
#         record = collection.find_one({"process_id": process_id, "_id": invoice_id})
#         if not record:
#             return {"error": "No data found for the given process_id and invoice_id"}
#         return convert_objectid(record)
#     else:
#         records = list(collection.find({"process_id": process_id}))
#         if not records:
#             return {"error": "No data found for the given process_id"}
#         return convert_objectid_for_status(records)

@app.get("/invoice-data/{process_id}/{invoice_id}")
def get_invoice_data(process_id: str , invoice_id: Optional[str]= None):
    if invoice_id:
        record = collection.find_one({"process_id": process_id, "_id": invoice_id})
        if not record:
            return {"error": "No data found for the given process_id and invoice_id"}

        invoice_date_str = record.get("Invoice Date", {}).get("value")
        start_date_str = record.get("start_date")
        end_date_str = record.get("end_date")
        file_name = record.get("filename", "N/A")

        # Check that all dates exist and are strings
        if invoice_date_str and isinstance(start_date_str, str) and isinstance(end_date_str, str):
            try:
                invoice_date = datetime.strptime(invoice_date_str, "%Y-%m-%d").date()
                promo_start = datetime.strptime(start_date_str, "%d-%m-%Y").date()
                promo_end = datetime.strptime(end_date_str, "%d-%m-%Y").date()

                if not (promo_start <= invoice_date <= promo_end):
                    return JSONResponse(content={
                        "message": "Uploaded invoice is NOT in the promo date range.",
                        "invoice_date": invoice_date_str,
                        "promo_start": start_date_str,
                        "promo_end": end_date_str,
                        "file_name": file_name
                    })
            except Exception as e:
                return JSONResponse(content={
                    "message": f"Date parsing error: {str(e)}",
                    "invoice_date": invoice_date_str,
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "file_name": file_name
                })

        return convert_objectid(record)

    else:
        records = list(collection.find({"process_id": process_id}))
        if not records:
            return {"error": "No data found for the given process_id"}
        return convert_objectid_for_status(records)

    
@app.get("/match-product")
def match_product(process_id: str = Header(None, description="Enter your process ID"), invoice_id: str = Header(None, description="Enter your invoice ID")):
    if not process_id:
        raise HTTPException(status_code=400, detail="Process ID and Invoice ID is required")
    
    logger.info(f"Received process ID: {process_id}")  # Debugging statement
    logger.info(f"Received invoice ID: {invoice_id}")  # Debugging statement

    # Fetch invoices with the provided app_key
    if (invoice_id):
        invoices = list(collection_invoices_data.find({
            "process_id": process_id,
            "_id": invoice_id
        }))
    else:
        invoices = list(collection_invoices_data.find({
            "process_id": process_id
        }))


    print(invoices)

    if not invoices:
        raise HTTPException(status_code=404, detail="No invoices found for the given app key")
    
    logger.info(f"Processing {invoices}")
    matched_results = []
    unmatched_results = []
    for invoice in invoices:
        database_id = invoice["_id"]
        file = preprocess([invoice])
        df = pd.read_csv(file)
        # df = preprocess()
        i = 0
        ct = 0
        matched = []
        unmatched = []

        for _, row in df.iterrows():
            i+=1
            logger.info(f"Number of descriptions processed: {i}, Number of matches found: {ct}")
            # print(row["Item Description"])
            item_description = str(row["Description without size"])*2 + 3 * str(row["Size Cleaned"]) if row["Size Cleaned"] != "N/A" else row["Item Description"]
            invoice_embedding = get_embedding(item_description.lower())

            matches = search_product_by_vector(invoice_embedding, str(row["Size Cleaned"]), collection_products)
            best_match = matches[0] if matches else None  # Extract the first match if available

            if best_match:
                ct += 1
                final_score = best_match.get("final_score", "N/A")

                matched_data = {
                    "file_name":row["File Name"],
                    "original_description": row["Item Description"],
                    "extracted_name": row["Description without size"],
                    "extracted_size": row["Size"],
                    "db_matched_name": best_match.get("label", "N/A"),
                    "db_matched_size": best_match.get("display_size", "N/A"),
                    "ean": best_match.get("ean", "N/A"),
                    "cai": best_match.get("cai", "N/A"),
                    "final_score": best_match.get("final_score", "N/A"),
                }

                if isinstance(database_id, str):
                    try:
                        # database_id = ObjectId(database_id)
                        logger.info(f"found database id: {database_id}")
                    except Exception as e:
                        logger.error(f"Invalid ObjectId: {database_id}, Error: {e}")
                        return JSONResponse(status_code=400, content={"detail": "Invalid database_id format."})

                matched.append(matched_data)
                # Convert database_ID to ObjectId if necessary
                # database_id = row["database_ID"]
                doc = collection_invoices_data.find_one({"_id": database_id})
                if not doc:
                    logger.error(f"No document found with _id: {database_id}")
                else:
                    logger.info("FOund ID: {database_id}")


                # if isinstance(database_id, str):
                #     try:
                #         database_id = ObjectId(database_id)
                #     except Exception as e:
                #         logger.error(f"Invalid ObjectId: {database_id}, Error: {e}")
                #         return JSONResponse(status_code=400, content={"detail": "Invalid database_id format."})

                item_number = row["Item number"]  # Example: "Invoice Item #1"
                update_path = f"{item_number}.Matched_Data"

                update_path = f"{item_number}.Matched Data"  # Dynamic field path

                if not collection_invoices_data.find_one({"_id":database_id}):
                    database_id = ObjectId(database_id)

                update_result = collection_invoices_data.update_one(
                    {"_id": database_id},
                    {"$set": {update_path: matched_data}}
                )
                logger.info(f"Updating document with _id: {database_id}, path: {update_path}")

                logger.info(f"Update Result: {update_result.raw_result}")
                if update_result.modified_count > 0:
                    logger.info(f"Updated document with _id: {database_id}")
                else:
                    logger.warning(f"No document found with _id: {database_id}")

            else:
                unmatched.append({
                    "file_name":row["File Name"],
                    "original_description": row["Item Description"],
                    "extracted_name": row["Description without size"],
                    "extracted_size" : row["Size"],
                    "db_matched_name": "No match found",
                    "db_matched_size": "N/A",
                    "ean": "N/A",
                    "cai": "N/A",
                    "final_score": "N/A"
                })

        matched_results.append(matched)
        unmatched_results.append(unmatched)


    # Convert results to DataFrame and save to CSV
    output_df = pd.DataFrame(matched_results)
    output_df.to_csv("matched_results.csv",index=False)
    def clean_dataframe(df):
        return df.rename(columns=lambda x: str(x).replace(" ", "_"))\
             .replace([np.inf, -np.inf], "")\
             .map(lambda x: "" if pd.isna(x) else x)
    

    flat_matched_results = [item for sublist in matched_results for item in sublist]  
    output_df = pd.DataFrame(flat_matched_results)

    if isinstance(output_df, pd.DataFrame):
        output_df = clean_dataframe(output_df).to_dict(orient="records")


    print("Matching complete. Results saved to matched_results.csv")
    print(f"Number of matches found = {ct}")

    return jsonable_encoder(output_df)


@app.get("/match-vendor")
def match_vendor(process_id: str = Header(None, description="Enter your process ID"), invoice_id: str = Header(None, description="Enter your invoice ID")):
    return ""
