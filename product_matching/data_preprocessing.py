import os
import re
import openai
# from dotenv import load_dotenv
import requests
import pandas as pd
import pymongo
from config.config import OPENAI_API_KEY

# load_dotenv()

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
# DATA_API_URL = os.getenv("DATA_API_URL")

# load_dotenv()

# MONGO_URI = os.getenv("MONGODB_URI")

# # MongoDB Connection
# client = pymongo.MongoClient(MONGO_URI)
# db = client.promo
# collection_products = db.products
# collection_invoices_data = db.invoices

def clean_text(text):
    """Remove extra spaces, special characters, and convert to uppercase."""
    text = re.sub(r"[^a-zA-Z0-9\s/\.\-\+]", "", text)  # Escape . and +
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
    return text.upper()

def extract_size(name):
    """Extract tire sizes from text, covering multiple formats."""
    size_pattern = r"\s*\d{3}/\d{2}\s*(?:Z\s*)?(?:R\s*)?(?:/\s*)?(?:X\s*)?\d{2}\s*(?:XL\s*)?\d{2,3}\s*[VWTYH]\s*(?:XL\s*)?"
    match = re.search(size_pattern, name)
    size = ''
    if match:
        size = match.group(0)
    else:
        size = "N/A"

     # Initialize an empty list to store matched terms
    extra_sizes = []
    
    # Check for terms and add them to extra_sizes
    for term in ["XL", "VOL", "ZP"]:
        if term in name and term not in size:
            extra_sizes.append(term)
            name = name.replace(term, '').strip()

    match = re.search(r"\s(N|S|MO|AO|CONNECT|NA)[012]?\s", name)
    if match:
        extra_sizes.append(match.group())  # Add the matched term
        name = re.sub(match.group(), '', name).strip()

    if '*' in name:
        extra_sizes.append("*")
        name = name.replace('*', '').strip()

    # Append all matched terms to size
    if extra_sizes:
        size = size + " " + " ".join(extra_sizes)

    return size

def clean_size(size):
    return re.sub(r'[^a-zA-Z0-9*.]', ' ', size).strip()

def get_embedding(text):
    response = openai.embeddings.create(input=[text], model="text-embedding-ada-002")
    return response.data[0].embedding  # Updated response format

def preprocess(invoices):
    # Fetch data from MongoDB
    
    processed_data = []
    for invoice in invoices:
        file_name = invoice.get("filename", "Customer Name")
        ID = invoice.get("_id")
        
        for key, item in invoice.items():
            if key.startswith("Invoice Item") and isinstance(item, dict):
                desc = item.get("Description", {}).get("value", "")
                cleaned_desc = clean_text(desc)
                size = extract_size(cleaned_desc)
                name = re.sub(size, "", cleaned_desc).strip() if size != "N/A" else cleaned_desc
                cleaned_size = clean_size(size) if size != "N/A" else ""
                
                processed_data.append([ID, key, file_name, desc, name, size, cleaned_size, f"{name} {size}" if size != "N/A" else name])
    # Save to CSV file
    output_file = "name_size.csv"
    df_output = pd.DataFrame(processed_data, columns=["database_ID", "Item number", "File Name", "Item Description", "Description without size", "Size", "Size Cleaned", "Key"])
    df_output.to_csv(output_file, index=False)

    return output_file
