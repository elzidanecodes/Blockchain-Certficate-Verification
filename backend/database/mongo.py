from pymongo import MongoClient
from datetime import datetime
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "certdb"
COLLECTION_cert = "cert_info"
COLLECTION_verify = "verify_logs"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection_cert = db[COLLECTION_cert]
collection_verify_logs = db[COLLECTION_verify]

# Index unik kombinasi certificate_id + contract_address
collection_cert.create_index(
    [("certificate_id", 1), ("contract_address", 1)],
    unique=True
)

def save_certificate_data(certificate_id, contract_address, encrypted_data_sertif, qr_base64, cert_base64):
    data = {
        "certificate_id": certificate_id,
        "contract_address": contract_address,
        "encrypted_data_sertif": encrypted_data_sertif,
        "qr_code_png": qr_base64,
        "certificate_png": cert_base64,
        "created_at": datetime.utcnow()
    }
    collection_cert.replace_one(
        {"certificate_id": certificate_id, "contract_address": contract_address},
        data,
        upsert=True
    )

def get_certificate_by_id(certificate_id, contract_address):
    return collection_cert.find_one({
        "certificate_id": certificate_id,
        "contract_address": contract_address
    })

def save_verify_log(data: dict):
    data["timestamp"] = datetime.utcnow()
    collection_verify_logs.insert_one(data)