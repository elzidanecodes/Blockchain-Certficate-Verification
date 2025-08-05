# celery_worker.py

from celery import Celery
import os
import numpy as np
import easyocr

from utils.verification_utils import process_single_certificate
import sys

# Tambahkan current directory ke sys.path (opsional jika diperlukan)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Setup Celery
celery = Celery(
    "tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

# Task untuk OCR async
@celery.task(name="tasks.run_ocr")
def run_ocr(file_path):
    reader = easyocr.Reader(["en", "id"], gpu=True)
    image_np = np.load(file_path)
    result = reader.readtext(image_np, detail=0)
    os.remove(file_path)
    return result

# Task untuk verifikasi lengkap async (OCR + hash + RSA + IPFS)
@celery.task(name="tasks.run_verifikasi")
def run_verifikasi(npy_path, filename, username):
    result = process_single_certificate(npy_path, filename, username)
    try:
        os.remove(npy_path)
    except Exception as e:
        print(f"❌ Gagal hapus file: {e}")
    return result
