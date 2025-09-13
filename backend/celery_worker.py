# celery_worker.py

from celery import Celery
import os
import numpy as np
import easyocr
import time

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

@celery.task(name="tasks.run_verifikasi")
def run_verifikasi(npy_path, filename, username):
    t0 = time.perf_counter()                     # ⬅️ start timer per sertifikat
    result = process_single_certificate(npy_path, filename, username)
    elapsed_ms = int((time.perf_counter() - t0) * 1000)  # ⬅️ hitung ms

    # sisipkan ke payload hasil agar tercatat (tidak mengganggu alur lain)
    try:
        if isinstance(result, dict):
            result["verification_time_ms"] = elapsed_ms
        else:
            result = {"status": "unknown", "verification_time_ms": elapsed_ms}
    except Exception:
        # fallback; jangan sampai gagal hanya karena pengayaan hasil
        result = {"status": "error_merging_result", "verification_time_ms": elapsed_ms}

    # housekeeping: hapus file temp
    try:
        os.remove(npy_path)
    except Exception as e:
        print(f"❌ Gagal hapus file: {e}")

    return result
