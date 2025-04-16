import os
from dotenv import load_dotenv
import pymongo

load_dotenv()

# # Azure credentials 
# endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
# key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

# Mongodb credentials 
MONGODB_URI = os.getenv("MONGODB_URI")
client = pymongo.MongoClient(MONGODB_URI)
db = client.promo
collection_products = db.products
collection_invoices_data = db.invoices

# folder dir
# UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")

# App_Key
APP_KEY = os.getenv("APP_KEY")

# Open-API-Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
