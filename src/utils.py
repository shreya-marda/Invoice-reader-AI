from bson import ObjectId
import zipfile
import io

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



def extract_zip_files(file_bytes):
    """
    Extract files from an in-memory ZIP archive.
    Returns a list of (filename, file_bytes) tuples.
    """
    extracted_files_data = []

    with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as zip_ref:
        extracted_files = [
            f for f in zip_ref.namelist()
            if not f.startswith("__MACOSX") and not f.endswith("/")
        ]
        for extracted_file in extracted_files:
            extracted_bytes = zip_ref.read(extracted_file)
            extracted_files_data.append((extracted_file, extracted_bytes))

    return extracted_files_data




