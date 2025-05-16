from pymongo import MongoClient
from datetime import datetime
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "certdb"
COLLECTION_NAME = "cert_info"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Index unik kombinasi certificate_id + contract_address
collection.create_index(
    [("certificate_id", 1), ("contract_address", 1)],
    unique=True
)

def save_certificate_data(certificate_id, contract_address, encrypted_info, qr_base64, cert_base64):
    data = {
        "certificate_id": certificate_id,
        "contract_address": contract_address,
        "encrypted_user_info": encrypted_info,
        "qr_code_png": qr_base64,
        "certificate_png": cert_base64,
        "created_at": datetime.utcnow()
    }
    collection.replace_one(
        {"certificate_id": certificate_id, "contract_address": contract_address},
        data,
        upsert=True
    )

def get_certificate_by_id(certificate_id, contract_address):
    return collection.find_one({
        "certificate_id": certificate_id,
        "contract_address": contract_address
    })

def save_verification_result(data):
    certificate_id = data.get("certificate_id")
    contract_address = data.get("contract_address")

    if not certificate_id or not contract_address:
        raise ValueError("certificate_id and contract_address are required for verification result")

    verification_data = {
        "verified_at": datetime.utcnow(),
        "image_base64": data.get("image_base64", ""),
        "hash": data.get("hash", ""),
        "valid": data.get("valid", False)
    }

    collection.update_one(
        {"certificate_id": certificate_id, "contract_address": contract_address},
        {"$set": {"verification_result": verification_data}},
        upsert=True
    )