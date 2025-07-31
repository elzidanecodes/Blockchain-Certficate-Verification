from celery import chain
import numpy as np
import tempfile
import os
import uuid

from utils.ocr_utils import run_ocr_and_extract
from utils.hash_utils import run_hashing
from utils.rsa_utils import run_signature_check
from utils.ipfs_utils import run_regenerate_ipfs
from utils.log_utils import run_logging


def jalankan_proses_verifikasi(img_np: np.ndarray, filename: str, username: str):
    # Simpan sementara sebagai .npy
    temp_dir = tempfile.gettempdir()
    unique_name = f"{uuid.uuid4().hex}_{filename.replace(' ', '_')}.npy"
    npy_path = os.path.join(temp_dir, unique_name)
    np.save(npy_path, img_np)

    # Jalankan pipeline Celery
    task_chain = chain(
        run_ocr_and_extract.s(npy_path),            
        run_hashing.s(),                  
        run_signature_check.s(),        
        run_regenerate_ipfs.s(),         
        run_logging.s()                  
    )

    task_chain.delay()

    return {
        "message": "Task verifikasi dikirim",
        "filename": filename,
        "task": unique_name
    }
